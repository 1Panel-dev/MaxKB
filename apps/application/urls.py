from django.urls import path

from . import views

app_name = "application"
urlpatterns = [
    path('application', views.Application.as_view(), name="application"),
    path('application/profile', views.Application.Profile.as_view()),
    path('application/authentication', views.Application.Authentication.as_view()),
    path('application/<str:application_id>/hit_test', views.Application.HitTest.as_view()),
    path('application/<str:application_id>/api_key', views.Application.ApplicationKey.as_view()),
    path("application/<str:application_id>/api_key/<str:api_key_id>",
         views.Application.ApplicationKey.Operate.as_view()),
    path('application/<str:application_id>', views.Application.Operate.as_view(), name='application/operate'),
    path('application/<str:application_id>/list_dataset', views.Application.ListApplicationDataSet.as_view(),
         name='application/dataset'),
    path('application/<str:application_id>/access_token', views.Application.AccessToken.as_view(),
         name='application/access_token'),
    path('application/<int:current_page>/<int:page_size>', views.Application.Page.as_view(), name='application_page'),
    path('application/<str:application_id>/chat/open', views.ChatView.Open.as_view()),
    path("application/chat/open", views.ChatView.OpenTemp.as_view()),
    path('application/<str:application_id>/chat', views.ChatView.as_view(), name='chats'),
    path('application/<str:application_id>/chat/<int:current_page>/<int:page_size>', views.ChatView.Page.as_view()),
    path('application/<str:application_id>/chat/<chat_id>', views.ChatView.Operate.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/', views.ChatView.ChatRecord.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<int:current_page>/<int:page_size>',
         views.ChatView.ChatRecord.Page.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<chat_record_id>',
         views.ChatView.ChatRecord.Operate.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<str:chat_record_id>/vote',
         views.ChatView.ChatRecord.Vote.as_view(),
         name=''),
    path(
        'application/<str:application_id>/chat/<chat_id>/chat_record/<str:chat_record_id>/dataset/<str:dataset_id>/document_id/<str:document_id>/improve',
        views.ChatView.ChatRecord.Improve.as_view(),
        name=''),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<str:chat_record_id>/improve',
         views.ChatView.ChatRecord.ChatRecordImprove.as_view()),
    path('application/chat_message/<str:chat_id>', views.ChatView.Message.as_view())

]
