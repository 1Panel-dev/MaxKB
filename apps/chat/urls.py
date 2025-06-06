from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/embed', views.ChatEmbedView.as_view()),
    path('application/authentication', views.Authentication.as_view()),
    path('profile', views.ApplicationProfile.as_view())
]
