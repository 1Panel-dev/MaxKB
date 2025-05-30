from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/embed', views.ChatEmbedView.as_view()),
]
