from django.urls import path

from . import views

app_name = 'application'

urlpatterns = [

    path('workspace/<str:workspace_id>/application', views.Application.as_view(), name='application'),
    path('workspace/<str:workspace_id>/application/import', views.Application.Import.as_view()),
    path('workspace/<str:workspace_id>/application/<int:current_page>/<int:page_size>',
         views.Application.Page.as_view(), name='application_page'),
    path('workspace/<str:workspace_id>/application/<str:application_id>', views.Application.Operate.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_key',
         views.ApplicationKey.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_stats',
         views.ApplicationStats.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_key/<str:api_key_id>',
         views.ApplicationKey.Operate.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/export', views.Application.Export.as_view()),

    path('workspace/<str:workspace_id>/application/<str:application_id>/work_flow_version',
         views.ApplicationVersionView.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/access_token',
         views.AccessToken.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/work_flow_version/<int:current_page>/<int:page_size>',
        views.ApplicationVersionView.Page.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/work_flow_version/<str:work_flow_version_id>',
        views.ApplicationVersionView.Operate.as_view()),
]
