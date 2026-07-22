from django.urls import path

from . import views

app_name = "system_manage"
# @formatter:off
# fmt: off
urlpatterns = [
    path('workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>/resource/<str:resource>', views.WorkSpaceUserResourcePermissionView.as_view()),
    path('workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>/resource/<str:resource>/<int:current_page>/<int:page_size>', views.WorkSpaceUserResourcePermissionView.Page.as_view()),
    path('workspace/<str:workspace_id>/resource_user_permission/resource/<str:target>/resource/<str:resource>', views.WorkspaceResourceUserPermissionView.as_view()),
    path('workspace/<str:workspace_id>/resource_user_permission/resource/<str:target>/resource/<str:resource>/<int:current_page>/<int:page_size>', views.WorkspaceResourceUserPermissionView.Page.as_view()),
    path('workspace/<str:workspace_id>/resource_mapping/<str:resource>/<str:resource_id>/<int:current_page>/<int:page_size>', views.ResourceMappingView.as_view()),
    path('workspace/<str:workspace_id>/mapping_resource/<str:resource>/<str:resource_id>/<int:current_page>/<int:page_size>', views.MappingResourceView.as_view()),
    path('email_setting', views.SystemSetting.Email.as_view()),
    path('profile', views.SystemProfile.as_view()),
    path('system/chat_user', views.SystemChatUserView.as_view()),
    path('system/chat_user/list', views.SystemChatUserView.List.as_view()),
    path('system/chat_user/batch_delete', views.SystemChatUserView.BatchDelete.as_view()),
    path("system/chat_user/batch_add_group", views.SystemChatUserView.BatchAddGroup.as_view()),
    path("system/chat_user/<str:user_id>", views.SystemChatUserView.Operate.as_view()),
    path("system/chat_user/<str:user_id>/re_password", views.SystemChatUserView.RePassword.as_view()),
    path("system/chat_user/user_manage/<int:current_page>/<int:page_size>", views.SystemChatUserView.Page.as_view()),
    path('system/chat_user/group/<str:user_group_id>', views.SystemChatUserView.GetUserListByGroup.as_view()),
    path('system/group', views.SystemChatUserGroupView.as_view()),
    path('system/group/<str:user_group_id>', views.SystemChatUserGroupView.Delete.as_view()),
    path('system/group/<str:user_group_id>/add_member', views.SystemChatUserGroupView.AddMember.as_view()),
    path('system/group/<str:user_group_id>/remove_member', views.SystemChatUserGroupView.RemoveMember.as_view()),
    path('system/group/<str:user_group_id>/user_list/<int:current_page>/<int:page_size>', views.SystemChatUserGroupView.UserList.as_view()),
]
