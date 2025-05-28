from django.urls import path

from . import views

app_name = 'application'

urlpatterns = [
    path('workspace/<str:workspace_id>/application', views.Application.as_view(), name='application'),
    path('workspace/<str:workspace_id>/application/<int:current_page>/<int:page_size>',
         views.Application.Page.as_view(), name='application_page'),
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_key',
         views.ApplicationKey.as_view())]
