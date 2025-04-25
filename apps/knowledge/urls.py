from django.urls import path

from . import views

app_name = "knowledge"
urlpatterns = [
    path('workspace/<str:workspace_id>/knowledge', views.KnowledgeView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/base', views.KnowledgeBaseView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/web', views.KnowledgeWebView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/lark', views.KnowledgeLarkView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/yuque', views.KnowledgeYuqueView.as_view()),
]
