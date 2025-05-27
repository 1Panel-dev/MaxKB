from django.urls import path

from . import views

app_name = 'application'

urlpatterns = [
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_key', views.ApplicationKey.as_view()),
]
