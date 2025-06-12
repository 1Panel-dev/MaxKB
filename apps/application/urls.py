from django.urls import path

from . import views

app_name = 'application'

urlpatterns = [

    path('workspace/<str:workspace_id>/application', views.ApplicationAPI.as_view(), name='application'),
    path('workspace/<str:workspace_id>/application/import', views.ApplicationAPI.Import.as_view()),
    path('workspace/<str:workspace_id>/application/<int:current_page>/<int:page_size>',
         views.ApplicationAPI.Page.as_view(), name='application_page'),
    path('workspace/<str:workspace_id>/application/<str:application_id>', views.ApplicationAPI.Operate.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_key',
         views.ApplicationKey.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_stats',
         views.ApplicationStats.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/application_key/<str:api_key_id>',
         views.ApplicationKey.Operate.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/export', views.ApplicationAPI.Export.as_view()),

    path('workspace/<str:workspace_id>/application/<str:application_id>/work_flow_version',
         views.ApplicationVersionView.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/access_token',
         views.AccessToken.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/add_knowledge',
         views.ApplicationChatRecordAddKnowledge.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/chat',
         views.ApplicationChat.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/chat/export',
         views.ApplicationChat.Export.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/chat/<int:current_page>/<int:page_size>',
         views.ApplicationChat.Page.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/chat/<str:chat_id>/chat_record',
        views.ApplicationChatRecord.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/chat/<str:chat_id>/chat_record/<str:chat_record_id>',
        views.ApplicationChatRecordOperateAPI.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/chat/<str:chat_id>/chat_record/<int:current_page>/<int:page_size>',
        views.ApplicationChatRecord.Page.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/chat/<str:chat_id>/chat_record/<str:chat_record_id>/improve',
        views.ApplicationChatRecordImprove.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/chat/<str:chat_id>/chat_record/<str:chat_record_id>/knowledge/<str:knowledge_id>/document/<str:document_id>/improve',
        views.ApplicationChatRecordImproveParagraph.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/chat/<str:chat_id>/chat_record/<str:chat_record_id>/knowledge/<str:knowledge_id>/document/<str:document_id>/paragraph/<str:paragraph_id>/improve',
        views.ApplicationChatRecordImproveParagraph.Operate.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/work_flow_version/<int:current_page>/<int:page_size>',
        views.ApplicationVersionView.Page.as_view()),
    path(
        'workspace/<str:workspace_id>/application/<str:application_id>/work_flow_version/<str:work_flow_version_id>',
        views.ApplicationVersionView.Operate.as_view()),
    path('workspace/<str:workspace_id>/application/<str:application_id>/open', views.OpenView.as_view()),
    path('chat_message/<str:chat_id>', views.ChatView.as_view()),

]
