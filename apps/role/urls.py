from django.urls import path

from . import views

app_name = "role"
# @formatter:off
# fmt: off
urlpatterns = [
    path('user/permissions', views.UserPermissionsView.as_view()),
    # More specific routes first, parameterized routes last
    path('system/role/template/<str:role_type>', views.RoleTemplateView.as_view()),
    path('system/role', views.RoleView.as_view()),
    path('system/role/<str:role_id>/remove_member/<str:user_relation_id>', views.RoleRemoveMemberView.as_view()),
    path('system/role/<str:role_id>/add_member', views.RoleAddMemberView.as_view()),
    path('system/role/<str:role_id>/user_list/<int:current_page>/<int:page_size>', views.RoleMemberView.as_view()),
    path('system/role/<str:role_id>/permission', views.RolePermissionView.as_view()),
    path('system/role/<str:role_id>', views.RoleOperateView.as_view()),
    # System resource management - Application
    path('system/resource/application/<int:current_page>/<int:page_size>', views.SystemApplicationView.as_view()),
    path('system/resource/application/<str:application_id>/export', views.SystemApplicationExportView.as_view()),
    path('system/resource/application/<str:application_id>/access_token', views.SystemApplicationAccessTokenView.as_view()),
    path('system/resource/application/<str:application_id>', views.SystemApplicationDeleteView.as_view()),
    # System resource management - Knowledge
    path('system/resource/knowledge/<int:current_page>/<int:page_size>', views.SystemKnowledgeView.as_view()),
    path('system/resource/knowledge/<str:knowledge_id>', views.SystemKnowledgeDeleteView.as_view()),
    # System resource management - Tool
    path('system/resource/tool/<int:current_page>/<int:page_size>', views.SystemToolView.as_view()),
    path('system/resource/tool/<str:tool_id>', views.SystemToolDeleteView.as_view()),
    # System resource management - Model
    path('system/resource/model/<int:current_page>/<int:page_size>', views.SystemModelView.as_view()),
    path('system/resource/model/<str:model_id>', views.SystemModelDeleteView.as_view()),
]
