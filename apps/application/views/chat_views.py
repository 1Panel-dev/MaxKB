# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_views.py
    @date：2023/11/14 9:53
    @desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from application.serializers.chat_message_serializers import ChatMessageSerializer, OpenAIChatSerializer
from application.serializers.chat_serializers import ChatSerializers, ChatRecordSerializer
from application.swagger_api.chat_api import ChatApi, VoteApi, ChatRecordApi, ImproveApi, ChatRecordImproveApi, \
    ChatClientHistoryApi, OpenAIChatApi
from application.views import get_application_operation_object
from common.auth import TokenAuth, has_permissions, OpenAIKeyAuth
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import Permission, Group, Operate, \
    RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.file_serializers import FileSerializer


class Openai(APIView):
    authentication_classes = [OpenAIKeyAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("OpenAI Interface Dialogue"),
                         operation_id=_("OpenAI Interface Dialogue"),
                         request_body=OpenAIChatApi.get_request_body_api(),
                         responses=OpenAIChatApi.get_response_body_api(),
                         tags=[_("OpenAI Dialogue")])
    def post(self, request: Request, application_id: str):
        return OpenAIChatSerializer(data={'application_id': application_id, 'client_id': request.auth.client_id,
                                          'client_type': request.auth.client_type}).chat(request.data)


class ChatView(APIView):
    authentication_classes = [TokenAuth]

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Export conversation"),
                             operation_id=_("Export conversation"),
                             manual_parameters=ChatApi.get_request_params_api(),
                             tags=[_("Application/Conversation Log")]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        @log(menu='Conversation Log', operate="Export conversation",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def post(self, request: Request, application_id: str):
            return ChatSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                      'user_id': request.user.id}).export(request.data)

    class Open(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the session id according to the application id"),
                             operation_id=_("Get the session id according to the application id"),
                             manual_parameters=ChatApi.OpenChat.get_request_params_api(),
                             tags=[_("Application/Chat")])
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN,
                            RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))],
                           compare=CompareConstants.AND)
        )
        def get(self, request: Request, application_id: str):
            return result.success(ChatSerializers.OpenChat(
                data={'user_id': request.user.id, 'application_id': application_id}).open())

    class OpenWorkFlowTemp(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the workflow temporary session id"),
                             operation_id=_("Get the workflow temporary session id"),
                             request_body=ChatApi.OpenWorkFlowTemp.get_request_body_api(),
                             responses=result.get_api_response(ChatApi.OpenTempChat.get_response_body_api()),
                             tags=[_("Application/Chat")])
        def post(self, request: Request):
            return result.success(ChatSerializers.OpenWorkFlowChat(
                data={'user_id': request.user.id, **request.data}).open())

    class OpenTemp(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get a temporary session id"),
                             operation_id=_("Get a temporary session id"),
                             request_body=ChatApi.OpenTempChat.get_request_body_api(),
                             responses=result.get_api_response(ChatApi.OpenTempChat.get_response_body_api()),
                             tags=[_("Application/Chat")])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def post(self, request: Request):
            return result.success(ChatSerializers.OpenTempChat(
                data={**request.data, 'user_id': request.user.id}).open())

    class Message(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("dialogue"),
                             operation_id=_("dialogue"),
                             request_body=ChatApi.get_request_body_api(),
                             tags=[_("Application/Chat")])
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY,
                            RoleConstants.APPLICATION_ACCESS_TOKEN],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def post(self, request: Request, chat_id: str):
            return ChatMessageSerializer(data={'chat_id': chat_id, 'message': request.data.get('message'),
                                               're_chat': (request.data.get(
                                                   're_chat') if 're_chat' in request.data else False),
                                               'stream': (request.data.get(
                                                   'stream') if 'stream' in request.data else True),
                                               'application_id': (request.auth.keywords.get(
                                                   'application_id') if request.auth.client_type == AuthenticationType.APPLICATION_ACCESS_TOKEN.value else None),
                                               'client_id': request.auth.client_id,
                                               'form_data': (request.data.get(
                                                   'form_data') if 'form_data' in request.data else {}),

                                               'image_list': request.data.get(
                                                   'image_list') if 'image_list' in request.data else [],
                                               'document_list': request.data.get(
                                                   'document_list') if 'document_list' in request.data else [],
                                               'audio_list': request.data.get(
                                                   'audio_list') if 'audio_list' in request.data else [],
                                               'other_list': request.data.get(
                                                   'other_list') if 'other_list' in request.data else [],
                                               'client_type': request.auth.client_type,
                                               'node_id': request.data.get('node_id', None),
                                               'runtime_node_id': request.data.get('runtime_node_id', None),
                                               'node_data': request.data.get('node_data', {}),
                                               'chat_record_id': request.data.get('chat_record_id'),
                                               'child_node': request.data.get('child_node')}
                                         ).chat()

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_("Get the conversation list"),
                         operation_id=_("Get the conversation list"),
                         manual_parameters=ChatApi.get_request_params_api(),
                         responses=result.get_api_array_response(ChatApi.get_response_body_api()),
                         tags=[_("Application/Conversation Log")]
                         )
    @has_permissions(
        ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                       [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                       dynamic_tag=keywords.get('application_id'))])
    )
    def get(self, request: Request, application_id: str):
        return result.success(ChatSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                  'user_id': request.user.id}).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_("Delete a conversation"),
                             operation_id=_("Delete a conversation"),
                             tags=[_("Application/Conversation Log")])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND),
            compare=CompareConstants.AND)
        @log(menu='Conversation Log', operate="Delete a conversation",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def delete(self, request: Request, application_id: str, chat_id: str):
            return result.success(
                ChatSerializers.Operate(
                    data={'application_id': application_id, 'user_id': request.user.id,
                          'chat_id': chat_id}).delete())

    class ClientChatHistoryPage(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get client conversation list by paging"),
                             operation_id=_("Get client conversation list by paging"),
                             manual_parameters=result.get_page_request_params(
                                 ChatClientHistoryApi.get_request_params_api()),
                             responses=result.get_page_api_response(ChatApi.get_response_body_api()),
                             tags=[_("Application/Conversation Log")]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.APPLICATION_ACCESS_TOKEN],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def get(self, request: Request, application_id: str, current_page: int, page_size: int):
            return result.success(ChatSerializers.ClientChatHistory(
                data={'client_id': request.auth.client_id, 'application_id': application_id}).page(
                current_page=current_page,
                page_size=page_size))

        class Operate(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['DELETE'], detail=False)
            @swagger_auto_schema(operation_summary=_("Client deletes conversation"),
                                 operation_id=_("Client deletes conversation"),
                                 tags=[_("Application/Conversation Log")])
            @has_permissions(ViewPermission(
                [RoleConstants.APPLICATION_ACCESS_TOKEN],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND),
                compare=CompareConstants.AND)
            @log(menu='Conversation Log', operate="Client deletes conversation",
                 get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
            def delete(self, request: Request, application_id: str, chat_id: str):
                return result.success(
                    ChatSerializers.Operate(
                        data={'application_id': application_id, 'user_id': request.user.id,
                              'chat_id': chat_id}).logic_delete())

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary=_("Client modifies dialogue summary"),
                                 operation_id=_("Client modifies dialogue summary"),
                                 request_body=ChatClientHistoryApi.Operate.ReAbstract.get_request_body_api(),
                                 responses=result.get_default_response(),
                                 tags=[_("Application/Conversation Log")])
            @has_permissions(ViewPermission(
                [RoleConstants.APPLICATION_ACCESS_TOKEN, RoleConstants.ADMIN, RoleConstants.USER],
                [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                dynamic_tag=keywords.get('application_id'))],
                compare=CompareConstants.AND),
                compare=CompareConstants.AND)
            @log(menu='Conversation Log', operate="Client modifies dialogue summary",
                 get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
            def put(self, request: Request, application_id: str, chat_id: str):
                return result.success(
                    ChatSerializers.Operate(
                        data={'application_id': application_id, 'user_id': request.user.id,
                              'chat_id': chat_id}).re_abstract(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get the conversation list by page"),
                             operation_id=_("Get the conversation list by page"),
                             manual_parameters=result.get_page_request_params(ChatApi.get_request_params_api()),
                             responses=result.get_page_api_response(ChatApi.get_response_body_api()),
                             tags=[_("Application/Conversation Log")]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def get(self, request: Request, application_id: str, current_page: int, page_size: int):
            return result.success(ChatSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                      'user_id': request.user.id}).page(current_page=current_page,
                                                        page_size=page_size))

    class ChatRecord(APIView):
        authentication_classes = [TokenAuth]

        class Operate(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['GET'], detail=False)
            @swagger_auto_schema(operation_summary=_("Get conversation record details"),
                                 operation_id=_("Get conversation record details"),
                                 manual_parameters=ChatRecordApi.get_request_params_api(),
                                 responses=result.get_api_array_response(ChatRecordApi.get_response_body_api()),
                                 tags=[_("Application/Conversation Log")]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY,
                                RoleConstants.APPLICATION_ACCESS_TOKEN],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))])
            )
            def get(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
                return result.success(ChatRecordSerializer.Operate(
                    data={'application_id': application_id,
                          'chat_id': chat_id,
                          'chat_record_id': chat_record_id}).one(request.auth.current_role))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_("Get a list of conversation records"),
                             operation_id=_("Get a list of conversation records"),
                             manual_parameters=ChatRecordApi.get_request_params_api(),
                             responses=result.get_api_array_response(ChatRecordApi.get_response_body_api()),
                             tags=[_("Application/Conversation Log")]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def get(self, request: Request, application_id: str, chat_id: str):
            return result.success(ChatRecordSerializer.Query(
                data={'application_id': application_id,
                      'chat_id': chat_id, 'order_asc': request.query_params.get('order_asc')}).list())

        class Page(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['GET'], detail=False)
            @swagger_auto_schema(operation_summary=_("Get the conversation history list by page"),
                                 operation_id=_("Get the conversation history list by page"),
                                 manual_parameters=result.get_page_request_params(
                                     ChatRecordApi.get_request_params_api()),
                                 responses=result.get_page_api_response(ChatRecordApi.get_response_body_api()),
                                 tags=[_("Application/Conversation Log")]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))])
            )
            def get(self, request: Request, application_id: str, chat_id: str, current_page: int, page_size: int):
                return result.success(ChatRecordSerializer.Query(
                    data={'application_id': application_id,
                          'chat_id': chat_id, 'order_asc': request.query_params.get('order_asc')}).page(current_page,
                                                                                                        page_size))

        class Vote(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary=_("Like, Dislike"),
                                 operation_id=_("Like, Dislike"),
                                 manual_parameters=VoteApi.get_request_params_api(),
                                 request_body=VoteApi.get_request_body_api(),
                                 responses=result.get_default_response(),
                                 tags=[_("Application/Chat")]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY,
                                RoleConstants.APPLICATION_ACCESS_TOKEN],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))])
            )
            @log(menu='Conversation Log', operate="Like, Dislike",
                 get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
            def put(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
                return result.success(ChatRecordSerializer.Vote(
                    data={'vote_status': request.data.get('vote_status'), 'chat_id': chat_id,
                          'chat_record_id': chat_record_id}).vote())

        class ChatRecordImprove(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['GET'], detail=False)
            @swagger_auto_schema(operation_summary=_("Get the list of marked paragraphs"),
                                 operation_id=_("Get the list of marked paragraphs"),
                                 manual_parameters=ChatRecordImproveApi.get_request_params_api(),
                                 responses=result.get_api_response(ChatRecordImproveApi.get_response_body_api()),
                                 tags=[_("Application/Conversation Log/Annotation")]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))]
                               ))
            def get(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
                return result.success(ChatRecordSerializer.ChatRecordImprove(
                    data={'chat_id': chat_id, 'chat_record_id': chat_record_id}).get())

        class Improve(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary=_("Annotation"),
                                 operation_id=_("Annotation"),
                                 manual_parameters=ImproveApi.get_request_params_api(),
                                 request_body=ImproveApi.get_request_body_api(),
                                 responses=result.get_api_response(ChatRecordApi.get_response_body_api()),
                                 tags=[_("Application/Conversation Log/Annotation")]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))],

                               ), ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                                 [lambda r, keywords: Permission(group=Group.DATASET,
                                                                                 operate=Operate.MANAGE,
                                                                                 dynamic_tag=keywords.get(
                                                                                     'dataset_id'))],
                                                 compare=CompareConstants.AND
                                                 ), compare=CompareConstants.AND)
            @log(menu='Conversation Log', operate="Annotation",
                 get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
            def put(self, request: Request, application_id: str, chat_id: str, chat_record_id: str, dataset_id: str,
                    document_id: str):
                return result.success(ChatRecordSerializer.Improve(
                    data={'chat_id': chat_id, 'chat_record_id': chat_record_id,
                          'dataset_id': dataset_id, 'document_id': document_id}).improve(request.data))

            @action(methods=['POST'], detail=False)
            @swagger_auto_schema(operation_summary=_("Add to Knowledge Base"),
                                 operation_id=_("Add to Knowledge Base"),
                                 manual_parameters=ImproveApi.get_request_params_api_post(),
                                 request_body=ImproveApi.get_request_body_api_post(),
                                 responses=result.get_default_response(),
                                 tags=[_("Application/Conversation Log/Add to Knowledge Base")]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))],

                               ), ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                                 [lambda r, keywords: Permission(group=Group.DATASET,
                                                                                 operate=Operate.MANAGE,
                                                                                 dynamic_tag=keywords.get(
                                                                                     'dataset_id'))],
                                                 compare=CompareConstants.AND
                                                 ), compare=CompareConstants.AND)
            @log(menu='Conversation Log', operate="Add to Knowledge Base",
                 get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
            def post(self, request: Request, application_id: str, dataset_id: str):
                return result.success(ChatRecordSerializer.PostImprove().post_improve(request.data))

            class Operate(APIView):
                authentication_classes = [TokenAuth]

                @action(methods=['DELETE'], detail=False)
                @swagger_auto_schema(operation_summary=_("Delete a Annotation"),
                                     operation_id=_("Delete a Annotation"),
                                     manual_parameters=ImproveApi.get_request_params_api(),
                                     responses=result.get_api_response(ChatRecordApi.get_response_body_api()),
                                     tags=[_("Application/Conversation Log/Annotation")]
                                     )
                @has_permissions(
                    ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                   [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                                   dynamic_tag=keywords.get('application_id'))],

                                   ), ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                                     [lambda r, keywords: Permission(group=Group.DATASET,
                                                                                     operate=Operate.MANAGE,
                                                                                     dynamic_tag=keywords.get(
                                                                                         'dataset_id'))],
                                                     compare=CompareConstants.AND
                                                     ), compare=CompareConstants.AND)
                @log(menu='Conversation Log', operate="Delete a Annotation",
                     get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
                def delete(self, request: Request, application_id: str, chat_id: str, chat_record_id: str,
                           dataset_id: str,
                           document_id: str, paragraph_id: str):
                    return result.success(ChatRecordSerializer.Improve.Operate(
                        data={'chat_id': chat_id, 'chat_record_id': chat_record_id,
                              'dataset_id': dataset_id, 'document_id': document_id,
                              'paragraph_id': paragraph_id}).delete())

    class UploadFile(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Upload files"),
                             operation_id=_("Upload files"),
                             manual_parameters=[
                                 openapi.Parameter(name='application_id',
                                                   in_=openapi.IN_PATH,
                                                   type=openapi.TYPE_STRING,
                                                   required=True,
                                                   description=_('Application ID')),
                                 openapi.Parameter(name='chat_id',
                                                   in_=openapi.IN_PATH,
                                                   type=openapi.TYPE_STRING,
                                                   required=True,
                                                   description=_('Conversation ID')),
                                 openapi.Parameter(name='file',
                                                   in_=openapi.IN_FORM,
                                                   type=openapi.TYPE_FILE,
                                                   required=True,
                                                   description=_('Upload file'))
                             ],
                             tags=[_("Application/Conversation Log")]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY,
                            RoleConstants.APPLICATION_ACCESS_TOKEN],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def post(self, request: Request, application_id: str, chat_id: str):
            files = request.FILES.getlist('file')
            file_ids = []
            debug = request.data.get("debug", "false").lower() == "true"
            meta = {'application_id': application_id, 'chat_id': chat_id, 'debug': debug}
            for file in files:
                file_url = FileSerializer(data={'file': file, 'meta': meta}).upload()
                file_ids.append({'name': file.name, 'url': file_url, 'file_id': file_url.split('/')[-1]})
            return result.success(file_ids)
