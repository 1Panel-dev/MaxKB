from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path('user/login', views.LoginView.as_view(), name='login'),
    path('user/profile', views.UserProfileView.as_view(), name="user_profile"),
    path('user/captcha', views.CaptchaView.as_view(), name='captcha'),
    path('user/test', views.TestPermissionsUserView.as_view(), name="test"),
    path('workspace/<str:workspace_id>/user/profile', views.TestWorkspacePermissionUserView.as_view(),
         name="test_workspace_id_permission")
]
