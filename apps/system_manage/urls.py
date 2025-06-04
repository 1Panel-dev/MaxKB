from django.urls import path

from . import views

app_name = "system_manage"
urlpatterns = [
    path('workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>',
         views.WorkSpaceUserResourcePermissionView.as_view()),
    path('email_setting', views.SystemSetting.Email.as_view()),
]
