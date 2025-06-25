import os

from django.urls import path

from . import views

app_name = "models_provider"
# @formatter:off
urlpatterns = [
    path('provider', views.Provide.as_view()),
    path('provider/model_type_list', views.Provide.ModelTypeList.as_view()),
    path('provider/model_list', views.Provide.ModelList.as_view()),
    path('provider/model_params_form', views.Provide.ModelParamsForm.as_view()),
    path('provider/model_form', views.Provide.ModelForm.as_view()),
    path('workspace/<str:workspace_id>/model', views.ModelSetting.as_view()),
    path('workspace/<str:workspace_id>/model_list', views.ModelList.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>/model_params_form', views.ModelSetting.ModelParamsForm.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>', views.ModelSetting.Operate.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>/pause_download', views.ModelSetting.PauseDownload.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>/meta', views.ModelSetting.ModelMeta.as_view()),
    path('system/shared/workspace/<str:workspace_id>/model', views.WorkspaceSharedModelSetting.as_view()),
]

if os.environ.get('SERVER_NAME', 'web') == 'local_model':
    urlpatterns += [
        path('model/<str:model_id>/embed_documents', views.ModelApply.EmbedDocuments.as_view()),
        path('model/<str:model_id>/embed_query', views.ModelApply.EmbedQuery.as_view()),
        path('model/<str:model_id>/compress_documents', views.ModelApply.CompressDocuments.as_view()),
    ]
