from django.urls import path

from . import views

app_name = 'oss'

urlpatterns = [
    path('file', views.FileView.as_view()),
    path('file/<str:file_id>', views.FileView.Operate.as_view()),
]
