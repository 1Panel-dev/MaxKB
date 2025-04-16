from django.urls import path

from . import views

app_name = "tool"
urlpatterns = [
    path('workspace/<str:workspace_id>/tool/create', views.ToolCreateView.as_view()),
]
