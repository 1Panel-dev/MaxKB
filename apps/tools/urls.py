from django.urls import path

from . import views

app_name = "tool"
# @formatter:off
urlpatterns = [
    path('workspace/internal/tool', views.ToolView.InternalTool.as_view()),
    path('workspace/store/tool', views.ToolView.StoreTool.as_view()),
    path('workspace/<str:workspace_id>/tool', views.ToolView.as_view()),
    path('workspace/<str:workspace_id>/tool/import', views.ToolView.Import.as_view()),
    path('workspace/<str:workspace_id>/tool/pylint', views.ToolView.Pylint.as_view()),
    path('workspace/<str:workspace_id>/tool/debug', views.ToolView.Debug.as_view()),
    path('workspace/<str:workspace_id>/tool/tool_list', views.ToolView.Query.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>', views.ToolView.Operate.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/edit_icon', views.ToolView.EditIcon.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/export', views.ToolView.Export.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/add_internal_tool', views.ToolView.AddInternalTool.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/add_store_tool', views.ToolView.AddStoreTool.as_view()),
    path('workspace/<str:workspace_id>/tool/<str:tool_id>/update_store_tool', views.ToolView.UpdateStoreTool.as_view()),
    path('workspace/<str:workspace_id>/tool/<int:current_page>/<int:page_size>', views.ToolView.Page.as_view()),
]
