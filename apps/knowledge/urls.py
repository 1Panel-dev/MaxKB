from django.urls import path

from . import views

app_name = "knowledge"
urlpatterns = [
    path('workspace/<str:workspace_id>/knowledge', views.KnowledgeView.as_view()),
]
