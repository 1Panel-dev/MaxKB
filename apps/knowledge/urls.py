from django.urls import path

from . import views

app_name = "knowledge"
urlpatterns = [
    path('workspace/<str:workspace_id>/knowledge', views.KnowledgeView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/base', views.KnowledgeBaseView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/web', views.KnowledgeWebView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>', views.KnowledgeView.Operate.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/split', views.DocumentView.Split.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<int:current_page>/<int:page_size>', views.KnowledgeView.Page.as_view()),
]
