from django.urls import path

from . import views

app_name = "system_manage"
# @formatter:off
urlpatterns = [
    path('workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>/resource/<str:resource>', views.WorkSpaceUserResourcePermissionView.as_view()),
    path('workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>/resource/<str:resource>/<int:current_page>/<int:page_size>', views.WorkSpaceUserResourcePermissionView.Page.as_view()),
    path('workspace/<str:workspace_id>/resource_user_permission/resource/<str:target>/resource/<str:resource>', views.WorkspaceResourceUserPermissionView.as_view()),
    path('workspace/<str:workspace_id>/resource_user_permission/resource/<str:target>/resource/<str:resource>/<int:current_page>/<int:page_size>', views.WorkspaceResourceUserPermissionView.Page.as_view()),
    path('workspace/<str:workspace_id>/resource_mapping/<str:resource>/<str:resource_id>/<int:current_page>/<int:page_size>', views.ResourceMappingView.as_view()),
    path('email_setting', views.SystemSetting.Email.as_view()),
    path('profile', views.SystemProfile.as_view()),
    path('valid/<str:valid_type>/<int:valid_count>', views.Valid.as_view())
]
