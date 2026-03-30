from django.urls import path

from . import views

app_name = "tool"
# @formatter:off
urlpatterns = [
    path('workspace/internal/tool', views.ToolView.InternalTool.as_view()),
    path('workspace/store/tool', views.ToolView.StoreTool.as_view()),
    path('workspace/<str:workspace_id>/tool', views.ToolView.as_view()),
    path('workspace/<str:workspace_id>/tool/workflow', views.ToolWorkflowView.as_view()),
    path('workspace/<str:workspace_id>/tool/import', views.ToolView.Import.as_view()),
    path('workspace/<str:workspace_id>/tool/pylint', views.ToolView.Pylint.as_view()),
    path('workspace/<str:workspace_id>/tool/debug', views.ToolView.Debug.as_view()),
    path('workspace/<str:workspace_id>/tool/tool_list', views.ToolView.Query.as_view()),
    path('workspace/<str:workspace_id>/tool/test_connection', views.ToolView.TestConnection.as_view()),
    path('workspace/<str:workspace_id>/tool/upload_skill_file', views.ToolView.UploadSkillFile.as_view()),
    path('workspace/<str:workspace_id>/tool/generate_code', views.ToolView.GenerateCode.as_view()),
    path('workspace/<str:workspace_id>/tool/batch_delete', views.ToolView.BatchDelete.as_view()),
    path('workspace/<str:workspace_id>/tool/batch_move', views.ToolView.BatchMove.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>', views.ToolView.Operate.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/publish', views.ToolWorkflowView.Publish.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/debug', views.ToolWorkflowDebugView.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/workflow', views.ToolWorkflowView.Operate.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/workflow/export', views.ToolWorkflowView.Export.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/edit_icon', views.ToolView.EditIcon.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/export', views.ToolView.Export.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/add_internal_tool', views.ToolView.AddInternalTool.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/add_store_tool', views.ToolView.AddStoreTool.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/update_store_tool', views.ToolView.UpdateStoreTool.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/tool_record/<str:record_id>', views.ToolView.ToolRecord.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/tool_record/<int:current_page>/<int:page_size>', views.ToolView.PageToolRecord.as_view()),
    path('workspace/<str:workspace_id>/tool/<int:current_page>/<int:page_size>', views.ToolView.Page.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/tool_version', views.ToolWorkflowVersionView.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/tool_version/<int:current_page>/<int:page_size>', views.ToolWorkflowVersionView.Page.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/tool_version/<str:tool_version_id>', views.ToolWorkflowVersionView.Operate.as_view()),

]
