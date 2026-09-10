# coding=utf-8
import uuid_utils.compat as uuid
from functools import reduce

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from application.workflow.tools import Reasoning
from knowledge.models import File
from models_provider.tools import get_model_instance_by_model_workspace_id


class VideoUnderstandNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default="custom", label=_("Model id type"))
    model_id_reference = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=True, label=_("Reference Field")
    )
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Role Setting"))
    prompt = serializers.CharField(required=True, label=_("Prompt word"))
    dialogue_number = serializers.IntegerField(required=True, label=_("Number of multi-round conversations"))
    dialogue_type = serializers.CharField(required=True, label=_("Conversation storage type"))
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))
    video_list = serializers.ListField(required=False, label=_("video"))
    model_params_setting = serializers.JSONField(required=False, default=dict, label=_("Model parameter settings"))
    model_setting = serializers.DictField(required=False, label="Model settings")


class VideoUnderstandNode(INode):
    serializer_class = VideoUnderstandNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "video-understand-node"

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        node_params = self.get_parameters()

        model_id = node_params.get("model_id")
        model_id_type = node_params.get("model_id_type", "custom")
        model_id_reference = node_params.get("model_id_reference")
        system = node_params.get("system", "")
        prompt = node_params.get("prompt", "")
        dialogue_number = node_params.get("dialogue_number", 0)
        dialogue_type = node_params.get("dialogue_type", "WORKFLOW")
        is_result = node_params.get("is_result", False)
        video_list_ref = node_params.get("video_list")
        model_params_setting = node_params.get("model_params_setting")
        model_setting = node_params.get("model_setting")

        workflow_type = self.get_workflow_type()
        if workflow_type in (WorkflowType.KNOWLEDGE, WorkflowType.TOOL):
            history_chat_record = []
            chat_id = None
            workspace_id = workflow_params.get("workspace_id")
        else:
            history_chat_record = workflow_params.get("history_chat_record", [])
            chat_id = workflow_params.get("chat_id")
            workspace_id = workflow_params.get("workspace_id")

        if model_setting is None:
            model_setting = {
                "reasoning_content_enable": False,
                "reasoning_content_end": "</think>",
                "reasoning_content_start": "<think>",
            }
        self.write_context("model_setting", model_setting)

        if model_id_type == "reference" and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                model_id_reference[0],
                model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get("model_id", model_id)
                model_params_setting = reference_data.get("model_params_setting")

        if model_id_type == "default":
            default_model_setting = workflow_params.get("default_model_setting").get("IMAGE") or {}
            if default_model_setting and isinstance(default_model_setting, dict):
                model_id = default_model_setting.get("model_id", model_id)
                model_params_setting = default_model_setting.get("model_params_setting")

        if not model_id:
            raise Exception(_("Model is not allowed to be empty"))

        video = None
        if video_list_ref:
            video = self.workflow_manage.get_reference_field(video_list_ref[0], video_list_ref[1:])

        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id, **(model_params_setting or {}))

        history_message_for_details = self._get_history_message_for_details(history_chat_record, dialogue_number)
        self.write_context(
            "history_message",
            [{"content": message.content, "role": message.type} for message in (history_message_for_details or [])],
        )

        question = self.workflow_manage.generate_prompt(prompt)
        self.write_context("question", question)

        system = self.workflow_manage.generate_prompt(system)
        self.write_context("system", system)

        history_message = self._get_history_message(history_chat_record, dialogue_number, chat_model)
        message_list = self._generate_message_list(chat_model, system, prompt, history_message, video)
        self.write_context(
            "message_list",
            [{"content": m.content, "role": m.type} for m in message_list],
        )

        self._generate_context_video(video)
        self.write_context("dialogue_type", dialogue_type)

        reasoning_content_id = str(uuid.uuid7())
        text_content_id = str(uuid.uuid7())

        node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.RUNNING)

        r = chat_model.stream(message_list)
        self._stream_response(
            r, chat_model, message_list, question, reasoning_content_id, text_content_id, node_info, is_result
        )

    def _stream_response(
        self, response, chat_model, message_list, question, reasoning_content_id, text_content_id, node_info, is_result
    ):
        model_setting = self.get_context("model_setting") or {}
        reasoning = Reasoning(
            model_setting.get("reasoning_content_start", "<think>"),
            model_setting.get("reasoning_content_end", "</think>"),
        )
        answer = ""
        reasoning_content = ""
        response_reasoning_content = False

        for chunk in response:
            self._check_cancelled()
            reasoning_chunk = reasoning.get_reasoning_content(chunk)
            content_chunk = reasoning_chunk.get("content")
            if "reasoning_content" in chunk.additional_kwargs:
                response_reasoning_content = True
                reasoning_content_chunk = chunk.additional_kwargs.get("reasoning_content", "")
            else:
                reasoning_content_chunk = reasoning_chunk.get("reasoning_content")
            answer += content_chunk
            if reasoning_content_chunk is None:
                reasoning_content_chunk = ""
            reasoning_content += reasoning_content_chunk

            if is_result:
                if isinstance(chunk.content, list):
                    for chunk_item in chunk.content:
                        text = chunk_item.get("text", "")
                        if text:
                            self.write(
                                TextContent(
                                    text_content_id, text, Status.RUNNING, node_info, Position(self.get_node_id())
                                )
                            )
                        if reasoning_content_chunk and model_setting.get("reasoning_content_enable", False):
                            self.write(
                                ReasoningContent(
                                    reasoning_content_id,
                                    reasoning_content_chunk,
                                    Status.RUNNING,
                                    node_info,
                                    Position(self.get_node_id()),
                                )
                            )
                else:
                    if content_chunk:
                        self.write(
                            TextContent(
                                text_content_id, content_chunk, Status.RUNNING, node_info, Position(self.get_node_id())
                            )
                        )
                    if reasoning_content_chunk and model_setting.get("reasoning_content_enable", False):
                        self.write(
                            ReasoningContent(
                                reasoning_content_id,
                                reasoning_content_chunk,
                                Status.RUNNING,
                                node_info,
                                Position(self.get_node_id()),
                            )
                        )

        reasoning_end = reasoning.get_end_reasoning_content()
        answer += reasoning_end.get("content")
        reasoning_content_chunk = ""
        if not response_reasoning_content:
            reasoning_content_chunk = reasoning_end.get("reasoning_content")
        if is_result:
            if reasoning_end.get("content"):
                self.write(
                    TextContent(
                        text_content_id,
                        reasoning_end.get("content"),
                        Status.RUNNING,
                        node_info,
                        Position(self.get_node_id()),
                    )
                )
            if reasoning_content_chunk and model_setting.get("reasoning_content_enable", False):
                self.write(
                    ReasoningContent(
                        reasoning_content_id,
                        reasoning_content_chunk,
                        Status.RUNNING,
                        node_info,
                        Position(self.get_node_id()),
                    )
                )

        self._write_final_context(chat_model, message_list, question, answer, reasoning_content)

    def _write_final_context(self, chat_model, message_list, question, answer, reasoning_content):
        message_tokens = chat_model.get_num_tokens_from_messages(message_list)
        answer_tokens = chat_model.get_num_tokens(answer)
        self.write_context("message_tokens", message_tokens)
        self.write_context("answer_tokens", answer_tokens)
        self.write_context("answer", answer)
        self.write_context("question", question)
        self.write_context("reasoning_content", reasoning_content)

    def _generate_context_video(self, video):
        if isinstance(video, str) and video.startswith("http"):
            self.write_context("video_list", [{"url": video}])
        elif video is not None and len(video) > 0:
            self.write_context("video_list", video)

    def _get_history_message_for_details(self, history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(
            lambda x, y: [*x, *y],
            [
                [
                    self._generate_history_human_message_for_details(history_chat_record[index]),
                    *self._generate_history_ai_message(history_chat_record[index]),
                ]
                for index in range(start_index if start_index > 0 else 0, len(history_chat_record))
            ],
            [],
        )
        return history_message

    def _generate_history_ai_message(self, chat_record):
        for val in chat_record.details.values():
            if self.node.id == val["node_id"] and "video_list" in val:
                if val["dialogue_type"] == "WORKFLOW":
                    return chat_record.get_ai_message()
                return [AIMessage(content=val["answer"])]
        return chat_record.get_ai_message()

    def _generate_history_human_message_for_details(self, chat_record):
        for data in chat_record.details.values():
            if self.node.id == data["node_id"] and "video_list" in data:
                video_list = data["video_list"] or []
                if len(video_list) == 0 or data["dialogue_type"] == "WORKFLOW":
                    return HumanMessage(content=chat_record.problem_text)
                file_id_list = []
                url_list = []
                for video in video_list:
                    if "file_id" in video:
                        file_id_list.append(video.get("file_id"))
                    elif "url" in video:
                        url_list.append(video.get("url"))
                return HumanMessage(
                    content=[
                        {"type": "text", "text": data["question"]},
                        *[
                            {"type": "video_url", "video_url": {"url": f"./oss/file/{file_id}"}}
                            for file_id in file_id_list
                        ],
                        *[{"type": "video_url", "video_url": {"url": url}} for url in url_list],
                    ]
                )
        return HumanMessage(content=chat_record.problem_text)

    def _get_history_message(self, history_chat_record, dialogue_number, video_model):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(
            lambda x, y: [*x, *y],
            [
                [
                    self._generate_history_human_message(history_chat_record[index], video_model),
                    *self._generate_history_ai_message(history_chat_record[index]),
                ]
                for index in range(start_index if start_index > 0 else 0, len(history_chat_record))
            ],
            [],
        )
        return history_message

    def _generate_history_human_message(self, chat_record, video_model):
        for data in chat_record.details.values():
            if self.node.id == data["node_id"] and "video_list" in data:
                video_list = data["video_list"] or []
                if len(video_list) == 0 or data["dialogue_type"] == "WORKFLOW":
                    return HumanMessage(content=chat_record.problem_text)
                file_id_list = []
                url_list = []
                for video in video_list:
                    if "file_id" in video:
                        file_id_list.append(video.get("file_id"))
                    elif "url" in video:
                        url_list.append(video.get("url"))
                video_base64_list = [self._file_id_to_base64(file_id, video_model) for file_id in file_id_list]
                return HumanMessage(
                    content=[
                        {"type": "text", "text": data["question"]},
                        *[
                            {"type": "video_url", "video_url": {"url": base64_video}}
                            for base64_video in video_base64_list
                        ],
                        *[{"type": "video_url", "video_url": {"url": url}} for url in url_list],
                    ]
                )
        return HumanMessage(content=chat_record.problem_text)

    @staticmethod
    def _file_id_to_base64(file_id: str, video_model):
        file = QuerySet(File).filter(id=file_id).first()
        file_bytes = file.get_bytes()
        return video_model.upload_file_and_get_url(file_bytes, file.file_name)

    def _process_videos(self, video, video_model):
        videos = []
        if isinstance(video, str) and video.startswith("http"):
            videos.append({"type": "video_url", "video_url": {"url": video}})
        elif video is not None and len(video) > 0:
            for v in video:
                if "file_id" in v:
                    file_id = v["file_id"]
                    file = QuerySet(File).filter(id=file_id).first()
                    url = video_model.upload_file_and_get_url(file.get_bytes(), file.file_name)
                    videos.append({"type": "video_url", "video_url": {"url": url}})
                elif "url" in v and v["url"].startswith("http"):
                    videos.append({"type": "video_url", "video_url": {"url": v["url"]}})
        return videos

    def _generate_message_list(self, video_model, system: str, prompt: str, history_message, video):
        prompt_text = self.workflow_manage.generate_prompt(prompt)
        videos = self._process_videos(video, video_model)

        if videos:
            messages = [HumanMessage(content=[{"type": "text", "text": prompt_text}, *videos])]
        else:
            messages = [HumanMessage(prompt_text)]

        if system is not None and len(system) > 0:
            return [SystemMessage(system), *history_message, *messages]
        else:
            return [*history_message, *messages]

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "question": self.get_context("question"),
                "answer": self.get_context("answer"),
                "video_list": self.get_context("video_list"),
                "reasoning_content": self.get_context("reasoning_content"),
                "message_tokens": self.get_context("message_tokens"),
                "answer_tokens": self.get_context("answer_tokens"),
            }
        )
        return details
