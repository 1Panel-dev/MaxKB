from django.urls import path

from . import views

app_name = "models_provider"
urlpatterns = [
    # path('provider/<str:provider>/<str:method>', views.Provide.Exec.as_view(), name='provide_exec'),
    path('provider', views.Provide.as_view(), name='provide'),
    path('provider/model_type_list', views.Provide.ModelTypeList.as_view(), name="provider/model_type_list"),
    path('provider/model_list', views.Provide.ModelList.as_view(), name="provider/model_name_list"),
    # path('provider/model_params_form', views.Provide.ModelParamsForm.as_view(),
    #      name="provider/model_params_form"),
    # path('provider/model_form', views.Provide.ModelForm.as_view(),
    #      name="provider/model_form"),
    path('workspace/<str:workspace_id>/model', views.Model.as_view(), name='model'),
    # path('workspace/<str:workspace_id>/model/<str:model_id>/model_params_form', views.Model.ModelParamsForm.as_view(),
    #      name='model/model_params_form'),
    # path('workspace/<str:workspace_id>/model/<str:model_id>', views.Model.Operate.as_view(), name='model/operate'),
    # path('workspace/<str:workspace_id>/model/<str:model_id>/pause_download', views.Model.PauseDownload.as_view(), name='model/operate'),
    # path('workspace/<str:workspace_id>/model/<str:model_id>/meta', views.Model.ModelMeta.as_view(), name='model/operate/meta'),
]
