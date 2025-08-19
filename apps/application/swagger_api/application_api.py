# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_key.py
    @date：2023/11/7 10:50
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _


class ApplicationApi(ApiMixin):
    class EditApplicationIcon(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='file',
                                  in_=openapi.IN_FORM,
                                  type=openapi.TYPE_FILE,
                                  required=True,
                                  description=_('Upload files'))
            ]

    class Authentication(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['access_token', ],
                properties={
                    'access_token': openapi.Schema(type=openapi.TYPE_STRING,
                                                   title=_("Application authentication token"),
                                                   description=_("Application authentication token")),

                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_STRING,
                title=_("Application authentication token"),
                description=_("Application authentication token"),
                default="token"
            )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'name', 'desc', 'model_id', 'dialogue_number', 'user_id', 'status', 'create_time',
                      'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description=_("Primary key id")),
                'name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Name"),
                                       description=_("Application Name")),
                'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Description"),
                                       description=_("Application Description")),
                'model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Model id"), description=_("Model id")),
                "dialogue_number": openapi.Schema(type=openapi.TYPE_NUMBER,
                                                  title=_("Number of multi-round conversations"),
                                                  description=_("Number of multi-round conversations")),
                'prologue': openapi.Schema(type=openapi.TYPE_STRING, title=_("Opening remarks"),
                                           description=_("Opening remarks")),
                'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                          title=_("Example List"), description=_("Example List")),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Affiliation user"),
                                          description=_("Affiliation user")),

                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is publish"), description=_('Is publish')),

                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Creation time"),
                                              description=_('Creation time')),

                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Modification time"),
                                              description=_('Modification time')),

                'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(type=openapi.TYPE_STRING),
                                                  title=_("List of associated knowledge base IDs"),
                                                  description=_(
                                                      "List of associated knowledge base IDs (returned when querying details)"))
            }
        )

    class Model(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID')),
                    openapi.Parameter(name='model_type', in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('Model Type')),
                    ]

    class ApiKey(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID'))

                    ]

        class Operate(ApiMixin):
            @staticmethod
            def get_request_params_api():
                return [openapi.Parameter(name='application_id',
                                          in_=openapi.IN_PATH,
                                          type=openapi.TYPE_STRING,
                                          required=True,
                                          description=_('Application ID')),
                        openapi.Parameter(name='api_key_id',
                                          in_=openapi.IN_PATH,
                                          type=openapi.TYPE_STRING,
                                          required=True,
                                          description=_('Application api_key id'))
                        ]

            @staticmethod
            def get_request_body_api():
                return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=[],
                    properties={
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is activation"),
                                                    description=_("Is activation")),
                        'allow_cross_domain': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                             title=_("Is cross-domain allowed"),
                                                             description=_("Is cross-domain allowed")),
                        'cross_domain_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_('Cross-domain list'),
                                                            items=openapi.Schema(type=openapi.TYPE_STRING))
                    }
                )

            @staticmethod
            def get_response_body_api():
                return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Primary key id"),
                                             description=_("Primary key id")),
                        'secret_key': openapi.Schema(type=openapi.TYPE_STRING, title=_("Secret key"),
                                                     description=_("Secret key")),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is activation"),
                                                    description=_("Is activation")),
                        'application_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application ID"),
                                                         description=_("Application ID")),
                        'allow_cross_domain': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                             title=_("Is cross-domain allowed"),
                                                             description=_("Is cross-domain allowed")),
                        'cross_domain_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_('Cross-domain list'),
                                                            items=openapi.Schema(type=openapi.TYPE_STRING))
                    }
                )

    class AccessToken(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID'))

                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'access_token_reset': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Reset Token"),
                                                         description=_("Reset Token")),

                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is activation"),
                                                description=_("Is activation")),
                    'access_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of visits"),
                                                 description=_("Number of visits")),
                    'white_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Whether to enable whitelist"),
                                                   description=_("Whether to enable whitelist")),
                    'white_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(type=openapi.TYPE_STRING), title=_("Whitelist"),
                                                 description=_("Whitelist")),
                    'show_source': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                  title=_("Whether to display knowledge sources"),
                                                  description=_("Whether to display knowledge sources")),
                    'language': openapi.Schema(type=openapi.TYPE_STRING,
                                               title=_("language"),
                                               description=_("language"))
                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Primary key id"),
                                         description=_("Primary key id")),
                    'access_token': openapi.Schema(type=openapi.TYPE_STRING, title=_("Access Token"),
                                                   description=_("Access Token")),
                    'access_token_reset': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Reset Token"),
                                                         description=_("Reset Token")),

                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is activation"),
                                                description=_("Is activation")),
                    'access_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of visits"),
                                                 description=_("Number of visits")),
                    'white_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Whether to enable whitelist"),
                                                   description=_("Whether to enable whitelist")),
                    'white_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(type=openapi.TYPE_STRING), title=_("Whitelist"),
                                                 description=_("Whitelist")),
                    'show_source': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                  title=_("Whether to display knowledge sources"),
                                                  description=_("Whether to display knowledge sources")),
                    'language': openapi.Schema(type=openapi.TYPE_STRING,
                                               title=_("language"),
                                               description=_("language"))
                }
            )

    class Edit(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Name"),
                                           description=_("Application Name")),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Description"),
                                           description=_("Application Description")),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Model id"),
                                               description=_("Model id")),
                    "dialogue_number": openapi.Schema(type=openapi.TYPE_NUMBER,
                                                      title=_("Number of multi-round conversations"),
                                                      description=_("Number of multi-round conversations")),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title=_("Opening remarks"),
                                               description=_("Opening remarks")),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title=_("List of associated knowledge base IDs"),
                                                      description=_("List of associated knowledge base IDs")),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Problem Optimization"),
                                                           description=_("Whether to enable problem optimization"),
                                                           default=True),
                    'icon': openapi.Schema(type=openapi.TYPE_STRING, title="icon",
                                           description="icon", default="/ui/favicon.ico"),
                    'type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Type"),
                                           description=_("Application Type   SIMPLE |  WORK_FLOW")),
                    'work_flow': ApplicationApi.WorkFlow.get_request_body_api(),
                    'problem_optimization_prompt': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  title=_('Question optimization tips'),
                                                                  description=_("Question optimization tips"),
                                                                  default=_(
                                                                      "() contains the user's question. Answer the guessed user's question based on the context ({question}) Requirement: Output a complete question and put it in the <data></data> tag")),
                    'tts_model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Text-to-speech model ID"),
                                                   description=_("Text-to-speech model ID")),
                    'stt_model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Speech-to-text model id"),
                                                   description=_("Speech-to-text model id")),
                    'stt_model_enable': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is speech-to-text enabled"),
                                                       description=_("Is speech-to-text enabled")),
                    'tts_model_enable': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is text-to-speech enabled"),
                                                       description=_("Is text-to-speech enabled")),
                    'tts_type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Text-to-speech type"),
                                               description=_("Text-to-speech type"))

                }
            )

    class WorkFlow(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[''],
                properties={
                    'nodes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                            title=_("Node List"), description=_("Node List"),
                                            default=[]),
                    'edges': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                            title=_('Connection List'), description=_("Connection List"),
                                            default=[]),

                }
            )

    class DatasetSetting(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[''],
                properties={
                    'top_n': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Reference segment number"),
                                            description=_("Reference segment number"),
                                            default=5),
                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title=_('Similarity'),
                                                 description=_("Similarity"),
                                                 default=0.6),
                    'max_paragraph_char_number': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                title=_('Maximum number of quoted characters'),
                                                                description=_("Maximum number of quoted characters"),
                                                                default=3000),
                    'search_mode': openapi.Schema(type=openapi.TYPE_STRING, title=_('Retrieval Mode'),
                                                  description="embedding|keywords|blend", default='embedding'),
                    'no_references_setting': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                            title=_('No reference segment settings'),
                                                            required=['status', 'value'],
                                                            properties={
                                                                'status': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                         title=_("state"),
                                                                                         description=_(
                                                                                             "ai_questioning|designated_answer"),
                                                                                         default='ai_questioning'),
                                                                'value': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                        title=_("value"),
                                                                                        description=_(
                                                                                            "ai_questioning: is the title, designated_answer: is the designated answer content"),
                                                                                        default='{question}'),
                                                            }),
                }
            )

    class ModelSetting(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['prompt'],
                properties={
                    'prompt': openapi.Schema(type=openapi.TYPE_STRING, title=_("Prompt word"),
                                             description=_("Prompt word"),
                                             default=_(("Known information:\n"
                                                        "{data}\n"
                                                        "Answer requirements:\n"
                                                        "- If you don't know the answer or don't get the answer, please answer \"No relevant information found in the knowledge base, it is recommended to consult relevant technical support or refer to official documents for operation\".\n"
                                                        "- Avoid mentioning that you got the knowledge from <data></data>.\n"
                                                        "- Please keep the answer consistent with the description in <data></data>.\n"
                                                        "- Please use markdown syntax to optimize the format of the answer.\n"
                                                        "- Please return the image link, link address and script language in <data></data> completely.\n"
                                                        "- Please answer in the same language as the question.\n"
                                                        "Question:\n"
                                                        "{question}"))),

                    'system': openapi.Schema(type=openapi.TYPE_STRING, title=_("System prompt words (role)"),
                                             description=_("System prompt words (role)")),
                    'no_references_prompt': openapi.Schema(type=openapi.TYPE_STRING,
                                                           title=_("No citation segmentation prompt"),
                                                           default="{question}",
                                                           description=_("No citation segmentation prompt"))

                }
            )

    class Publish(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'work_flow': ApplicationApi.WorkFlow.get_request_body_api()
                }
            )

    class Create(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_id', 'dialogue_number', 'dataset_setting', 'model_setting',
                          'problem_optimization', 'stt_model_enable', 'stt_model_enable', 'tts_type',
                          'work_flow'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Name"),
                                           description=_("Application Name")),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Description"),
                                           description=_("Application Description")),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Model id"),
                                               description=_("Model id")),
                    "dialogue_number": openapi.Schema(type=openapi.TYPE_NUMBER,
                                                      title=_("Number of multi-round conversations"),
                                                      description=_("Number of multi-round conversations")),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title=_("Opening remarks"),
                                               description=_("Opening remarks")),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title=_("List of associated knowledge base IDs"),
                                                      description=_("List of associated knowledge base IDs")),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Problem Optimization"),
                                                           description=_("Problem Optimization"), default=True),
                    'type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Type"),
                                           description=_("Application Type   SIMPLE |  WORK_FLOW")),
                    'problem_optimization_prompt': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  title=_('Question optimization tips'),
                                                                  description=_("Question optimization tips"),
                                                                  default=_(
                                                                      "() contains the user's question. Answer the guessed user's question based on the context ({question}) Requirement: Output a complete question and put it in the <data></data> tag")),
                    'tts_model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Text-to-speech model ID"),
                                                   description=_("Text-to-speech model ID")),
                    'stt_model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Speech-to-text model id"),
                                                   description=_("Speech-to-text model id")),
                    'stt_model_enable': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is speech-to-text enabled"),
                                                       description=_("Is speech-to-text enabled")),
                    'tts_model_enable': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is text-to-speech enabled"),
                                                       description=_("Is text-to-speech enabled")),
                    'tts_type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Text-to-speech type"),
                                               description=_("Text-to-speech type")),
                    'work_flow': ApplicationApi.WorkFlow.get_request_body_api(),
                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'model_id', 'dialogue_number', 'dataset_setting', 'model_setting',
                          'problem_optimization', 'stt_model_enable', 'stt_model_enable', 'tts_type',
                          'work_flow'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Primary key id"),
                                         description=_("Primary key id")),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Name"),
                                           description=_("Application Name")),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Description"),
                                           description=_("Application Description")),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Model id"),
                                               description=_("Model id")),
                    "dialogue_number": openapi.Schema(type=openapi.TYPE_NUMBER,
                                                      title=_("Number of multi-round conversations"),
                                                      description=_("Number of multi-round conversations")),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title=_("Opening remarks"),
                                               description=_("Opening remarks")),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title=_("List of associated knowledge base IDs"),
                                                      description=_("List of associated knowledge base IDs")),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Problem Optimization"),
                                                           description=_("Problem Optimization"), default=True),
                    'type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application Type"),
                                           description=_("Application Type   SIMPLE |  WORK_FLOW")),
                    'problem_optimization_prompt': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  title=_('Question optimization tips'),
                                                                  description=_("Question optimization tips"),
                                                                  default=_(
                                                                      "() contains the user's question. Answer the guessed user's question based on the context ({question}) Requirement: Output a complete question and put it in the <data></data> tag")),
                    'tts_model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Text-to-speech model ID"),
                                                   description=_("Text-to-speech model ID")),
                    'stt_model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Speech-to-text model id"),
                                                   description=_("Speech-to-text model id")),
                    'stt_model_enable': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is speech-to-text enabled"),
                                                       description=_("Is speech-to-text enabled")),
                    'tts_model_enable': openapi.Schema(type=openapi.TYPE_STRING, title=_("Is text-to-speech enabled"),
                                                       description=_("Is text-to-speech enabled")),
                    'tts_type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Text-to-speech type"),
                                               description=_("Text-to-speech type")),
                    'work_flow': ApplicationApi.WorkFlow.get_request_body_api(),
                }
            )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('Application Name')),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('Application Description'))
                    ]

    class Export(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID')),

                    ]

    class Import(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='file',
                                      in_=openapi.IN_FORM,
                                      type=openapi.TYPE_FILE,
                                      required=True,
                                      description=_('Upload image files'))
                    ]

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID')),

                    ]

    class TextToSpeech(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID')),

                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'text': openapi.Schema(type=openapi.TYPE_STRING, title=_("Text"),
                                           description=_("Text")),
                }
            )
