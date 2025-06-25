from django.urls import path

from . import views

app_name = "system_manage"
# @formatter:off
urlpatterns = [
    path('workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>', views.WorkSpaceUserResourcePermissionView.as_view()),
    path('email_setting', views.SystemSetting.Email.as_view()),
    path('profile', views.SystemProfile.as_view()),
    path('valid/<str:valid_type>/<int:valid_count>', views.Valid.as_view())
]
