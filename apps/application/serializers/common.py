# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2025/6/9 13:42
    @desc:
"""
import json
from typing import List

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from application.chat_pipeline.step.chat_step.i_chat_step import PostResponseHandler
from application.models import Application, ChatRecord, Chat, ApplicationVersion, ChatUserType, ApplicationTypeChoices, \
    ApplicationKnowledgeMapping
from application.serializers.application_chat import ChatCountSerializer
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.encoder.encoder import SystemEncoder
from common.exception.app_exception import ChatException
from knowledge.models import Document
from models_provider.models import Model
from models_provider.tools import get_model_credential


class ChatInfo:
    def __init__(self,
                 chat_id: str,
                 chat_user_id: str,
                 chat_user_type: str,
                 knowledge_id_list: List[str],
                 exclude_document_id_list: list[str],
                 application_id: str,
                 debug=False):
        """
        :param chat_id:                     对话id
        :param chat_user_id                 对话用户id
        :param chat_user_type               对话用户类型
        :param knowledge_id_list:           知识库列表
        :param exclude_document_id_list:    排除的文档
        :param application_id               应用id
        :param debug                        是否是调试
        """
        self.chat_id = chat_id
        self.chat_user_id = chat_user_id
        self.chat_user_type = chat_user_type
        self.knowledge_id_list = knowledge_id_list
        self.exclude_document_id_list = exclude_document_id_list
        self.application_id = application_id
        self.chat_record_list: List[ChatRecord] = []
        self.application = None
        self.chat_user = None
        self.debug = debug

    @staticmethod
    def get_no_references_setting(knowledge_setting, model_setting):
        no_references_setting = knowledge_setting.get(
            'no_references_setting', {
                'status': 'ai_questioning',
                'value': '{question}'})
        if no_references_setting.get('status') == 'ai_questioning':
            no_references_prompt = model_setting.get('no_references_prompt', '{question}')
            no_references_setting['value'] = no_references_prompt if len(no_references_prompt) > 0 else "{question}"
        return no_references_setting

    def get_application(self):
        if self.debug:
            application = QuerySet(Application).filter(id=self.application_id).first()
            if not application:
                raise ChatException(500, _('The application does not exist'))
        else:
            application = QuerySet(ApplicationVersion).filter(application_id=self.application_id).order_by(
                '-create_time')[0:1].first()
            if not application:
                raise ChatException(500, _("The application has not been published. Please use it after publishing."))
        if application.type == ApplicationTypeChoices.SIMPLE.value:
            # 数据集id列表
            knowledge_id_list = [str(row.knowledge_id) for row in
                                 QuerySet(ApplicationKnowledgeMapping).filter(
                                     application_id=self.application_id)]

            # 需要排除的文档
            exclude_document_id_list = [str(document.id) for document in
                                        QuerySet(Document).filter(
                                            knowledge_id__in=knowledge_id_list,
                                            is_active=False)]
            self.knowledge_id_list = knowledge_id_list
            self.exclude_document_id_list = exclude_document_id_list
        self.application = application
        return application

    def get_chat_user(self, asker=None):
        if self.chat_user:
            return self.chat_user
        chat_user_model = DatabaseModelManage.get_model("chat_user")
        if self.chat_user_type == ChatUserType.CHAT_USER.value and chat_user_model:
            chat_user = QuerySet(chat_user_model).filter(id=self.chat_user_id).first()
            return {
                'id': str(chat_user.id),
                'email': chat_user.email,
                'phone': chat_user.phone,
                'nick_name': chat_user.nick_name,
                'username': chat_user.username,
                'source': chat_user.source
            }
        else:
            if asker:
                if isinstance(asker, dict):
                    self.chat_user = asker
                else:
                    self.chat_user = {'username': asker}
            else:
                self.chat_user = {'username': '游客'}
        return self.chat_user

    def to_base_pipeline_manage_params(self):
        self.get_application()
        self.get_chat_user()
        knowledge_setting = self.application.knowledge_setting
        model_setting = self.application.model_setting
        model_id = self.application.model_id
        model_params_setting = None
        if model_id is not None:
            model = QuerySet(Model).filter(id=model_id).first()
            credential = get_model_credential(model.provider, model.model_type, model.model_name)
            model_params_setting = credential.get_model_params_setting_form(model.model_name).get_default_form_data()
        return {
            'knowledge_id_list': self.knowledge_id_list,
            'exclude_document_id_list': self.exclude_document_id_list,
            'exclude_paragraph_id_list': [],
            'top_n': 3 if knowledge_setting.get('top_n') is None else knowledge_setting.get('top_n'),
            'similarity': 0.6 if knowledge_setting.get('similarity') is None else knowledge_setting.get('similarity'),
            'max_paragraph_char_number': knowledge_setting.get('max_paragraph_char_number') or 5000,
            'history_chat_record': self.chat_record_list,
            'chat_id': self.chat_id,
            'dialogue_number': self.application.dialogue_number,
            'problem_optimization_prompt': self.application.problem_optimization_prompt if self.application.problem_optimization_prompt is not None and len(
                self.application.problem_optimization_prompt) > 0 else _(
                "() contains the user's question. Answer the guessed user's question based on the context ({question}) Requirement: Output a complete question and put it in the <data></data> tag"),
            'prompt': model_setting.get(
                'prompt') if 'prompt' in model_setting and len(model_setting.get(
                'prompt')) > 0 else Application.get_default_model_prompt(),
            'system': model_setting.get(
                'system', None),
            'model_id': model_id,
            'problem_optimization': self.application.problem_optimization,
            'stream': True,
            'model_setting': model_setting,
            'model_params_setting': model_params_setting if self.application.model_params_setting is None or len(
                self.application.model_params_setting.keys()) == 0 else self.application.model_params_setting,
            'search_mode': self.application.knowledge_setting.get('search_mode') or 'embedding',
            'no_references_setting': self.get_no_references_setting(self.application.knowledge_setting, model_setting),
            'workspace_id': self.application.workspace_id,
            'application_id': self.application_id,
            'mcp_enable': self.application.mcp_enable,
            'mcp_tool_ids': self.application.mcp_tool_ids,
            'mcp_servers': self.application.mcp_servers,
            'mcp_source': self.application.mcp_source,
            'tool_enable': self.application.tool_enable,
            'tool_ids': self.application.tool_ids,
            'mcp_output_enable': self.application.mcp_output_enable,
        }

    def to_pipeline_manage_params(self, problem_text: str, post_response_handler: PostResponseHandler,
                                  exclude_paragraph_id_list, chat_user_id: str, chat_user_type, stream=True,
                                  form_data=None):
        if form_data is None:
            form_data = {}
        params = self.to_base_pipeline_manage_params()
        return {**params, 'problem_text': problem_text, 'post_response_handler': post_response_handler,
                'exclude_paragraph_id_list': exclude_paragraph_id_list, 'stream': stream, 'chat_user_id': chat_user_id,
                'chat_user_type': chat_user_type, 'form_data': form_data}

    def set_chat(self, question):
        if not self.debug:
            if not QuerySet(Chat).filter(id=self.chat_id).exists():
                Chat(id=self.chat_id, application_id=self.application_id, abstract=question[0:1024],
                     chat_user_id=self.chat_user_id, chat_user_type=self.chat_user_type,
                     asker=self.get_chat_user()).save()

    def set_chat_variable(self, chat_context):
        if not self.debug:
            chat = QuerySet(Chat).filter(id=self.chat_id).first()
            if chat:
                chat.meta = {**(chat.meta if isinstance(chat.meta, dict) else {}), **chat_context}
                chat.save()
        else:
            cache.set(Cache_Version.CHAT_VARIABLE.get_key(key=self.chat_id), chat_context,
                      version=Cache_Version.CHAT_VARIABLE.get_version(),
                      timeout=60 * 30)

    def get_chat_variable(self):
        if not self.debug:
            chat = QuerySet(Chat).filter(id=self.chat_id).first()
            if chat:
                return chat.meta
            return {}
        else:
            return cache.get(Cache_Version.CHAT_VARIABLE.get_key(key=self.chat_id),
                             version=Cache_Version.CHAT_VARIABLE.get_version()) or {}

    def append_chat_record(self, chat_record: ChatRecord):
        chat_record.problem_text = chat_record.problem_text[0:10240] if chat_record.problem_text is not None else ""
        chat_record.answer_text = chat_record.answer_text[0:40960] if chat_record.problem_text is not None else ""
        is_save = True
        # 存入缓存中
        for index in range(len(self.chat_record_list)):
            record = self.chat_record_list[index]
            if record.id == chat_record.id:
                self.chat_record_list[index] = chat_record
                is_save = False
                break
        if is_save:
            self.chat_record_list.append(chat_record)
        if not self.debug:
            if not QuerySet(Chat).filter(id=self.chat_id).exists():
                Chat(id=self.chat_id, application_id=self.application_id, abstract=chat_record.problem_text[0:1024],
                     chat_user_id=self.chat_user_id, chat_user_type=self.chat_user_type,
                     asker=self.get_chat_user()).save()
            else:
                QuerySet(Chat).filter(id=self.chat_id).update(update_time=timezone.now())
            # 插入会话记录
            chat_record.save()
            ChatCountSerializer(data={'chat_id': self.chat_id}).update_chat()

    def to_dict(self):

        return {
            'chat_id': self.chat_id,
            'chat_user_id': self.chat_user_id,
            'chat_user_type': self.chat_user_type,
            'knowledge_id_list': self.knowledge_id_list,
            'exclude_document_id_list': self.exclude_document_id_list,
            'application_id': self.application_id,
            'chat_record_list': [self.chat_record_to_map(c) for c in self.chat_record_list][-20:],
            'debug': self.debug
        }

    def chat_record_to_map(self, chat_record):
        return {'id': chat_record.id,
                'chat_id': chat_record.chat_id,
                'vote_status': chat_record.vote_status,
                'problem_text': chat_record.problem_text,
                'answer_text': chat_record.answer_text,
                'answer_text_list': chat_record.answer_text_list,
                'message_tokens': chat_record.message_tokens,
                'answer_tokens': chat_record.answer_tokens,
                'const': chat_record.const,
                'details': chat_record.details,
                'improve_paragraph_id_list': chat_record.improve_paragraph_id_list,
                'run_time': chat_record.run_time,
                'index': chat_record.index}

    @staticmethod
    def map_to_chat_record(chat_record_dict):
        return ChatRecord(id=chat_record_dict.get('id'),
                          chat_id=chat_record_dict.get('chat_id'),
                          vote_status=chat_record_dict.get('vote_status'),
                          problem_text=chat_record_dict.get('problem_text'),
                          answer_text=chat_record_dict.get('answer_text'),
                          answer_text_list=chat_record_dict.get('answer_text_list'),
                          message_tokens=chat_record_dict.get('message_tokens'),
                          answer_tokens=chat_record_dict.get('answer_tokens'),
                          const=chat_record_dict.get('const'),
                          details=chat_record_dict.get('details'),
                          improve_paragraph_id_list=chat_record_dict.get('improve_paragraph_id_list'),
                          run_time=chat_record_dict.get('run_time'),
                          index=chat_record_dict.get('index'), )

    def set_cache(self):
        cache.set(Cache_Version.CHAT.get_key(key=self.chat_id), self.to_dict(),
                  version=Cache_Version.CHAT_INFO.get_version(),
                  timeout=60 * 30)

    @staticmethod
    def map_to_chat_info(chat_info_dict):
        c = ChatInfo(chat_info_dict.get('chat_id'), chat_info_dict.get('chat_user_id'),
                     chat_info_dict.get('chat_user_type'), chat_info_dict.get('knowledge_id_list'),
                     chat_info_dict.get('exclude_document_id_list'),
                     chat_info_dict.get('application_id'),
                     debug=chat_info_dict.get('debug'))
        c.chat_record_list = [ChatInfo.map_to_chat_record(c_r) for c_r in chat_info_dict.get('chat_record_list')]
        return c

    @staticmethod
    def get_cache(chat_id):
        chat_info_dict = cache.get(Cache_Version.CHAT.get_key(key=chat_id),
                                   version=Cache_Version.CHAT_INFO.get_version())
        if chat_info_dict:
            return ChatInfo.map_to_chat_info(chat_info_dict)
        return None
