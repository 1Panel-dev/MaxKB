from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path('user/login', views.LoginView.as_view(), name='login'),
    path('user/profile', views.UserProfileView.as_view(), name="user_profile"),
    path('user/captcha', views.CaptchaView.as_view(), name='captcha'),
    path('user/test', views.TestPermissionsUserView.as_view(), name="test"),
    path('workspace/<str:workspace_id>/user/profile', views.TestWorkspacePermissionUserView.as_view(),
         name="test_workspace_id_permission"),
    path("user_manage", views.UserManage.as_view(), name="user_manage"),
    # path("user_manage/<str:user_id>", views.UserManage.Operate.as_view(), name="user_manage_operate"),
    # path("user_manage/<str:user_id>/re_password", views.UserManage.RePassword.as_view(),
    #      name="user_manage_re_password"),
    # path("user_manage/<int:current_page>/<int:page_size>", views.UserManage.Page.as_view(),
    #      name="user_manage_re_password"),
]
