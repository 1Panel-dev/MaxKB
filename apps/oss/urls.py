from django.urls import path

from . import views

app_name = 'oss'

urlpatterns = [
    path('oss/file', views.FileView.as_view()),
    path('oss/get_url/<str:application_id>', views.GetUrlView.as_view()),
]
