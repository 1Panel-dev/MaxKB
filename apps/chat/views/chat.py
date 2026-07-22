# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat.py
    @date：2025/6/6 11:18
    @desc:
"""
import json

import requests
from django.core.cache import cache
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import SpeechToTextAPI, TextToSpeechAPI
from application.models import ChatUserType, ChatSourceChoices
from chat.api.chat_api import ChatAPI
from chat.api.chat_authentication_api import ChatAuthenticationAPI, ChatAuthenticationProfileAPI, ChatOpenAPI, OpenAIAPI
from chat.serializers.chat import OpenChatSerializers, ChatSerializers, SpeechToTextSerializers, \
    TextToSpeechSerializers, OpenAIChatSerializer
from chat.serializers.chat_authentication import AnonymousAuthenticationSerializer, ApplicationProfileSerializer, \
    AuthProfileSerializer
from common.auth import ChatTokenAuth
from common.auth.common import FileToken
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import ChatAuth
from common.exception.app_exception import AppAuthenticationFailed, AppApiException
from common.log.log import _get_ip_address, log
from common.result import result
from common.utils.rsa_util import decrypt
from knowledge.models import FileSourceType
from maxkb.const import CONFIG
from models_provider.api.model import DefaultModelResponse
from oss.serializers.file import FileSerializer
from system_manage.serializers.chat_user import RePasswordSerializer, ChatUserProfileSerializer
from system_manage.serializers.chat_user_serializer import ChatUserAccessTokenSerializer
from users.api import CaptchaAPI, LoginAPI
from users.api.user import ResetPasswordAPI, UserProfileAPI
from users.serializers.login import CaptchaSerializer
from users.views import get_re_password_details


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
        ip_address = _get_ip_address(request)
        if application_id != str(request.auth.application_id):
            raise AppAuthenticationFailed(500, _('Secret key is invalid'))
        return OpenAIChatSerializer(
            data={'application_id': application_id, 'chat_user_id': request.auth.chat_user_id,
                  'chat_user_type': request.auth.chat_user_type,
                  'ip_address': ip_address,
                  'source': {"type": ChatSourceChoices.API_CALL.value}}).chat(request.data)


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
        token, f_token = AnonymousAuthenticationSerializer(
            data={'access_token': request.data.get("access_token")}).auth(
            request)
        response = result.success(
            token,
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                     "Access-Control-Allow-Methods": "POST",
                     "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}
        )
        secure = request.is_secure()
        response.set_cookie(
            'mk_file_auth',
            value=f_token,
            max_age=7 * 24 * 3600,
            path=f'{CONFIG.get_chat_path()}/{request.data.get("access_token")}',
            domain=None,
            secure=secure,
            httponly=True,
            samesite='Lax',
        )
        return response


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
        ip_address = _get_ip_address(request)
        return ChatSerializers(data={'chat_id': chat_id,
                                     'chat_user_id': request.auth.chat_user_id,
                                     'chat_user_type': request.auth.chat_user_type,
                                     'application_id': request.auth.application_id,
                                     'debug': False,
                                     'ip_address': ip_address,
                                     'source': {
                                         'type': ChatSourceChoices.API_CALL.value if request.auth.chat_user_type == ChatUserType.APPLICATION_API_KEY.value else ChatSourceChoices.ONLINE.value}
                                     }
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
        ip_address = _get_ip_address(request)
        return result.success(OpenChatSerializers(
            data={'application_id': request.auth.application_id,
                  'chat_user_id': request.auth.chat_user_id, 'chat_user_type': request.auth.chat_user_type,
                  'ip_address': ip_address,
                  'source': {
                      'type': ChatSourceChoices.API_CALL.value if request.auth.chat_user_type == ChatUserType.APPLICATION_API_KEY.value else ChatSourceChoices.ONLINE.value},
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
                data={'file': file, 'meta': meta, 'source_id': chat_id, 'source_type': FileSourceType.CHAT, }).upload(
                request.auth.chat_user_id)
            file_ids.append({'name': file.name, 'url': file_url, 'file_id': file_url.split('/')[-1]})
        return result.success(file_ids)


class ResetCurrentUserPasswordView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Modify current user password"),
        description=_("Modify current user password"),
        operation_id=_("Modify current user password"),  # type: ignore
        tags=[_("Chat User")],  # type: ignore
        request=ResetPasswordAPI.get_request(),
        responses=DefaultModelResponse.get_response(),
    )
    @log(
        menu="Chat User",
        operate="Modify current user password",
        get_operation_object=lambda r, k: {"name": r.user.username},
        get_details=get_re_password_details,
    )
    def post(self, request: Request):
        request_data = request.data
        encrypted_data = request_data.get("encryptedData", "")
        if encrypted_data:
            try:
                decrypted_raw = decrypt(encrypted_data)
                # decrypt 可能返回非 JSON 字符串，防护解析异常
                decrypted_data = json.loads(decrypted_raw) if decrypted_raw else {}
                if isinstance(decrypted_data, dict):
                    request_data = decrypted_data
            except Exception as e:
                raise AppApiException(500, _("Invalid encrypted data"))
        serializer_obj = RePasswordSerializer(data=request_data)
        if serializer_obj.reset_password(request.user.id):
            version, get_key = Cache_Version.CHAT_USER_TOKEN.value
            auth = request.META.get("HTTP_AUTHORIZATION")
            cache.delete(get_key(token=auth), version=version)
            return result.success(True)
        return result.error(_("Failed to change password"))



class ChatUserProfileView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get current user information"),
        description=_("Get current user information"),
        operation_id=_("Get current user information"),  # type: ignore
        tags=[_("Chat User")],  # type: ignore
        responses=UserProfileAPI.get_response(),
    )
    def get(self, request: Request):
        return result.success(ChatUserProfileSerializer().profile(request.user))


class BaseAuthView(APIView):
    @staticmethod
    def create_token_and_cache(access_token, user, request):
        token = ChatUserAccessTokenSerializer.create_token_and_cache(access_token, user, request)
        version, get_key = Cache_Version.CHAT_USER_TOKEN.value
        cache.set(get_key(token), user, timeout=60 * 60 * 2, version=version)
        return token, FileToken(str(user.id), AuthenticationType.CHAT_USER.value).to_token()

    @classmethod
    def generate(self, request, f_token: str, response: HttpResponse, path: str = '/chat'):
        secure = request.is_secure()
        response.set_cookie(
            "mk_file_auth",
            value=f_token,
            max_age=7 * 24 * 3600,
            path=path,
            domain=None,
            secure=secure,
            httponly=True,
            samesite="Lax",
        )
        return response


class LocalLoginView(BaseAuthView):
    @extend_schema(
        methods=["POST"],
        description=_("Log in"),
        summary=_("Log in"),
        operation_id=_("Log in"),  # type: ignore
        tags=[_("Chat User/login")],  # type: ignore
        request=LoginAPI.get_request(),
        responses=LoginAPI.get_response(),
    )
    def post(self, request: Request, access_token: str = None):
        user = ChatUserAccessTokenSerializer.local_login(request.data, access_token)
        user.source = "LOCAL"
        token, f_token = self.create_token_and_cache(access_token, user, request)
        response = result.success({'token': token})
        return self.generate(request, f_token, response, path=f'/chat/{access_token}/')


class Logout(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Sign out"),
        description=_("Sign out"),
        operation_id=_("Sign out"),  # type: ignore
        tags=[_("Chat User")],  # type: ignore
        responses=DefaultModelResponse.get_response(),
    )
    @log(menu="Chat User/logout", operate="Sign out", get_operation_object=lambda r, k: {"name": r.user.username})
    def post(self, request: Request):
        version, get_key = Cache_Version.CHAT_USER_TOKEN.value
        auth = request.META.get("HTTP_AUTHORIZATION")
        cache.delete(get_key(token=auth[7:]), version=version)
        return result.success(True)

