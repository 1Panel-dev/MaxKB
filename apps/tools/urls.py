from django.urls import path

from . import views

app_name = "tool"
urlpatterns = [
    path('workspace/<str:workspace_id>/tool', views.ToolView.Create.as_view()),
    path('workspace/<str:workspace_id>/tool', views.ToolTreeView.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>', views.ToolView.Operate.as_view()),
]
