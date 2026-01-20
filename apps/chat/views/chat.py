# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat.py
    @date：2025/6/6 11:18
    @desc:
"""
import requests
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import SpeechToTextAPI, TextToSpeechAPI
from chat.api.chat_api import ChatAPI
from chat.api.chat_authentication_api import ChatAuthenticationAPI, ChatAuthenticationProfileAPI, ChatOpenAPI, OpenAIAPI
from chat.serializers.chat import OpenChatSerializers, ChatSerializers, SpeechToTextSerializers, \
    TextToSpeechSerializers, OpenAIChatSerializer
from chat.serializers.chat_authentication import AnonymousAuthenticationSerializer, ApplicationProfileSerializer, \
    AuthProfileSerializer
from common.auth import ChatTokenAuth
from common.constants.permission_constants import ChatAuth
from common.exception.app_exception import AppAuthenticationFailed
from common.result import result
from knowledge.models import FileSourceType
from oss.serializers.file import FileSerializer
from users.api import CaptchaAPI
from users.serializers.login import CaptchaSerializer


def stream_image(response):
    """生成器函数，用于流式传输图片数据"""
    for chunk in response.iter_content(chunk_size=4096):
        if chunk:  # 过滤掉保持连接的空块
            yield chunk


class ResourceProxy(APIView):
    def get(self, request: Request):
        image_url = request.query_params.get("url")
        if not image_url:
            return result.error("Missing 'url' parameter")
        try:

            # 发送GET请求，流式获取图片内容
            response = requests.get(
                image_url,
                stream=True,  # 启用流式响应
                allow_redirects=True,
                timeout=10
            )
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            # 创建Django流式响应
            django_response = StreamingHttpResponse(
                stream_image(response),  # 使用生成器
                content_type=content_type
            )

            return django_response
        except Exception as e:
            return result.error(f"Image request failed: {str(e)}")


class OpenAIView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('OpenAI Interface Dialogue'),
        summary=_('OpenAI Interface Dialogue'),
        operation_id=_('OpenAI Interface Dialogue'),  # type: ignore
        request=OpenAIAPI.get_request(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request, application_id: str):
        return OpenAIChatSerializer(data={'application_id': application_id, 'chat_user_id': request.auth.chat_user_id,
                                          'chat_user_type': request.auth.chat_user_type}).chat(request.data)


class AnonymousAuthentication(APIView):
    def options(self, request, *args, **kwargs):
        return HttpResponse(
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                     "Access-Control-Allow-Methods": "POST",
                     "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}, )

    @extend_schema(
        methods=['POST'],
        description=_('Application Anonymous Certification'),
        summary=_('Application Anonymous Certification'),
        operation_id=_('Application Anonymous Certification'),  # type: ignore
        request=ChatAuthenticationAPI.get_request(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request):
        return result.success(
            AnonymousAuthenticationSerializer(data={'access_token': request.data.get("access_token")}).auth(
                request),
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                     "Access-Control-Allow-Methods": "POST",
                     "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}
        )


class ApplicationProfile(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get application related information"),
        summary=_("Get application related information"),
        operation_id=_("Get application related information"),  # type: ignore
        request=None,
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        if isinstance(request.auth, ChatAuth):
            return result.success(ApplicationProfileSerializer(
                data={'application_id': request.auth.application_id}).profile())
        raise AppAuthenticationFailed(401, "身份异常")


class AuthProfile(APIView):
    @extend_schema(
        methods=['GET'],
        description=_("Get application authentication information"),
        summary=_("Get application authentication information"),
        operation_id=_("Get application authentication information"),  # type: ignore
        parameters=ChatAuthenticationProfileAPI.get_parameters(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        return result.success(
            AuthProfileSerializer(data={'access_token': request.query_params.get("access_token")}).profile())


class ChatView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("dialogue"),
        summary=_("dialogue"),
        operation_id=_("dialogue"),  # type: ignore
        request=ChatAPI.get_request(),
        parameters=ChatAPI.get_parameters(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request, chat_id: str):
        return ChatSerializers(data={'chat_id': chat_id,
                                     'chat_user_id': request.auth.chat_user_id,
                                     'chat_user_type': request.auth.chat_user_type,
                                     'application_id': request.auth.application_id,
                                     'debug': False}
                               ).chat(request.data)


class OpenView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get the session id according to the application id"),
        summary=_("Get the session id according to the application id"),
        operation_id=_("Get the session id according to the application id"),  # type: ignore
        parameters=ChatOpenAPI.get_parameters(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        return result.success(OpenChatSerializers(
            data={'application_id': request.auth.application_id,
                  'chat_user_id': request.auth.chat_user_id, 'chat_user_type': request.auth.chat_user_type,
                  'debug': False}).open())


class CaptchaView(APIView):
    @extend_schema(methods=['GET'],
                   summary=_("Get Chat captcha"),
                   description=_("Get Chat captcha"),
                   operation_id=_("Get Chat captcha"),  # type: ignore
                   tags=[_("Chat")],  # type: ignore
                   responses=CaptchaAPI.get_response())
    def get(self, request: Request):
        username = request.query_params.get('username', None)
        accessToken = request.query_params.get('accessToken', None)
        return result.success(CaptchaSerializer().chat_generate(username, 'chat', accessToken))


class SpeechToText(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("speech to text"),
        summary=_("speech to text"),
        operation_id=_("speech to text"),  # type: ignore
        request=SpeechToTextAPI.get_request(),
        responses=SpeechToTextAPI.get_response(),
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request):
        return result.success(
            SpeechToTextSerializers(
                data={'application_id': request.auth.application_id})
            .speech_to_text({'file': request.FILES.get('file')}))


class TextToSpeech(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("text to speech"),
        summary=_("text to speech"),
        operation_id=_("text to speech"),  # type: ignore
        request=TextToSpeechAPI.get_request(),
        responses=TextToSpeechAPI.get_response(),
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request):
        byte_data = TextToSpeechSerializers(
            data={'application_id': request.auth.application_id}).text_to_speech(request.data)
        return HttpResponse(byte_data, status=200, headers={'Content-Type': 'audio/mp3',
                                                            'Content-Disposition': 'attachment; filename="abc.mp3"'})


class UploadFile(APIView):
    authentication_classes = [ChatTokenAuth]
    parser_classes = [MultiPartParser]

    @extend_schema(
        methods=['POST'],
        description=_("Upload files"),
        summary=_("Upload files"),
        operation_id=_("Upload files"),  # type: ignore
        request=TextToSpeechAPI.get_request(),
        responses=TextToSpeechAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    def post(self, request: Request, chat_id: str):
        files = request.FILES.getlist('file')
        file_ids = []
        meta = {}
        for file in files:
            file_url = FileSerializer(
                data={'file': file, 'meta': meta, 'source_id': chat_id, 'source_type': FileSourceType.CHAT, }).upload()
            file_ids.append({'name': file.name, 'url': file_url, 'file_id': file_url.split('/')[-1]})
        return result.success(file_ids)
