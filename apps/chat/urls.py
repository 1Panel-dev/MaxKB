from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/embed', views.ChatEmbedView.as_view()),
    path('application/anonymous_authentication', views.AnonymousAuthentication.as_view()),
    path('auth/profile', views.AuthProfile.as_view()),
    path('profile', views.ApplicationProfile.as_view()),
    path('chat_message/<str:chat_id>', views.ChatView.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/open', views.OpenView.as_view())
]
