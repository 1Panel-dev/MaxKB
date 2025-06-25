from django.urls import path

from . import views

app_name = "user"
# @formatter:off
urlpatterns = [
    path('user/login', views.LoginView.as_view(), name='login'),
    path('user/profile', views.UserProfileView.as_view(), name="user_profile"),
    path('user/captcha', views.CaptchaView.as_view(), name='captcha'),
    path('user/test', views.TestPermissionsUserView.as_view(), name="test"),
    path('user/logout', views.Logout.as_view(), name='logout'),
    path('user/language', views.SwitchUserLanguageView.as_view(), name='language'),
    path("user/send_email", views.SendEmail.as_view(), name='send_email'),
    path("user/check_code", views.CheckCode.as_view(), name='check_code'),
    path("user/re_password", views.RePasswordView.as_view(), name='re_password'),
    path("user/current/send_email", views.SendEmailToCurrentUserView.as_view(), name="send_email_current"),
    path("user/current/reset_password", views.ResetCurrentUserPasswordView.as_view(), name="reset_password_current"),
    path("user/list", views.UserList.as_view(), name="current_user_profile"),
    path('workspace/<str:workspace_id>/user_list', views.WorkspaceUserListView.as_view(), name="test_workspace_id_permission"),
    path('workspace/<str:workspace_id>/user_member',views.WorkspaceUserMemberView.as_view(), name="test_workspace_id_permission"),
    path('workspace/<str:workspace_id>/user/profile', views.TestWorkspacePermissionUserView.as_view(), name="test_workspace_id_permission"),
    path("user_manage", views.UserManage.as_view(), name="user_manage"),
    path("user_manage/batch_delete", views.UserManage.BatchDelete.as_view()),
    path("user_manage/password", views.UserManage.Password.as_view()),
    path("user_manage/<str:user_id>", views.UserManage.Operate.as_view(), name="user_manage_operate"),
    path("user_manage/<str:user_id>/re_password", views.UserManage.RePassword.as_view(), name="user_manage_re_password"),
    path("user_manage/<int:current_page>/<int:page_size>", views.UserManage.Page.as_view(), name="user_manage_page"),
]
