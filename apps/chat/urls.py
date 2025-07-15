from django.urls import path

from . import views

app_name = 'chat'
# @formatter:off
urlpatterns = [
    path('embed', views.ChatEmbedView.as_view()),
    path('auth/anonymous', views.AnonymousAuthentication.as_view()),
    path('profile', views.AuthProfile.as_view()),
    path('application/profile', views.ApplicationProfile.as_view(), name='profile'),
    path('chat_message/<str:chat_id>', views.ChatView.as_view(), name='chat'),
    path('open', views.OpenView.as_view(), name='open'),
    path('text_to_speech', views.TextToSpeech.as_view()),
    path('speech_to_text', views.SpeechToText.as_view()),
    path('captcha', views.CaptchaView.as_view(), name='captcha'),
    path('<str:application_id>/chat/completions', views.OpenAIView.as_view(),
         name='application/chat_completions'),
    path('vote/chat/<str:chat_id>/chat_record/<str:chat_record_id>', views.VoteView.as_view(), name='vote'),
    path('historical_conversation', views.HistoricalConversationView.as_view(), name='historical_conversation'),
    path('historical_conversation/<str:chat_id>/record/<str:chat_record_id>',views.ChatRecordView.as_view(),name='conversation_details'),
    path('historical_conversation/<int:current_page>/<int:page_size>', views.HistoricalConversationView.PageView.as_view(), name='historical_conversation'),
    path('historical_conversation/clear',views.HistoricalConversationView.BatchDelete.as_view(), name='historical_conversation_clear'),
    path('historical_conversation/<str:chat_id>',views.HistoricalConversationView.Operate.as_view(), name='historical_conversation_operate'),
    path('historical_conversation_record/<str:chat_id>', views.HistoricalConversationRecordView.as_view(), name='historical_conversation_record'),
    path('historical_conversation_record/<str:chat_id>/<int:current_page>/<int:page_size>', views.HistoricalConversationRecordView.PageView.as_view(), name='historical_conversation_record')
]
