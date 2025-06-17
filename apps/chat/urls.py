from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('embed', views.ChatEmbedView.as_view()),
    path('auth/anonymous', views.AnonymousAuthentication.as_view()),
    path('profile', views.AuthProfile.as_view()),
    path('application/profile', views.ApplicationProfile.as_view()),
    path('chat_message/<str:chat_id>', views.ChatView.as_view()),
    path('open', views.OpenView.as_view())
]
