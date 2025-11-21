import os

from django.urls import path

from . import views

app_name = "local_model"
# @formatter:off
urlpatterns = [
    path('model/validate', views.LocalModelApply.Validate.as_view()),
    path('model/<str:model_id>/embed_documents', views.LocalModelApply.EmbedDocuments.as_view()),
    path('model/<str:model_id>/embed_query', views.LocalModelApply.EmbedQuery.as_view()),
    path('model/<str:model_id>/compress_documents', views.LocalModelApply.CompressDocuments.as_view()),
    path('model/<str:model_id>/unload', views.LocalModelApply.Unload.as_view()),
    ]
