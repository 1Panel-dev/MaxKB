from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    path('portal', views.PortalView.as_view()),
]
