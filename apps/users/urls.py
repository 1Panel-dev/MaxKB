from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path('user', views.User.as_view(), name="profile"),
    path('user/list', views.User.Query.as_view()),
    path('user/login', views.Login.as_view(), name='login'),
    path('user/logout', views.Logout.as_view(), name='logout'),
    path('user/register', views.Register.as_view(), name="register"),
    path("user/send_email", views.SendEmail.as_view(), name='send_email'),
    path("user/check_code", views.CheckCode.as_view(), name='check_code'),
    path("user/re_password", views.RePasswordView.as_view(), name='re_password'),
    path("user/current/send_email", views.SendEmailToCurrentUserView.as_view(), name="send_email_current"),
    path("user/current/reset_password", views.ResetCurrentUserPasswordView.as_view(), name="reset_password_current")
]
