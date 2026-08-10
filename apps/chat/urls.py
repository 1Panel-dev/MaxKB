from django.urls import path, include

from application.views import ChatRecordDetailView, ChatRecordLinkView
from chat.views import v2 as v2_views, v3 as v3_views

app_name = 'chat'
# @formatter:off
# fmt: off

v3=[
 # ---- application 作用域：application_id 从 path 获取 ----
 path('application/<str:application_id>/',  include([
  path("profile",v3_views.ApplicationProfile.as_view(), name='v3_profile'),
  path('open', v3_views.OpenView.as_view(), name='v3_open'),
  path('text_to_speech',v3_views.TextToSpeech.as_view(),name='v3_text_to_speech'),
  path('speech_to_text',v3_views.SpeechToText.as_view(),name='v3_speech_to_text'),
  path('chat/completions',v3_views.OpenAIView.as_view(), name='v3_chat_completions'),
  path('chat/clear',v3_views.HistoricalConversationView.BatchDelete.as_view(), name='v3_historical_conversation_clear'),
  path('chat',v3_views.HistoricalConversationView.as_view(), name='v3_historical_conversation'),
  path('chat/<int:current_page>/<int:page_size>',v3_views.HistoricalConversationView.PageView.as_view(),name='v3_historical_conversation_page'),
  path('chat/<str:chat_id>/chat_message',v3_views.ChatView.as_view(), name='v3_chat'),
  path('chat/<str:chat_id>/chat_record',v3_views.HistoricalConversationRecordView.as_view(), name='v3_historical_conversation_record'),
  path('chat/<str:chat_id>/chat_record/<int:current_page>/<int:page_size>', v3_views.HistoricalConversationRecordView.PageView.as_view(), name='v3_historical_conversation_record_page'),
  path('chat/<str:chat_id>/chat_record/<str:chat_record_id>',v3_views.ChatRecordView.as_view(),name='v3_conversation_details'),
  path('chat/<str:chat_id>/chat_record/<str:chat_record_id>/vote',v3_views.VoteView.as_view(), name='v3_vote'),
  path('chat/<str:chat_id>/share_chat',ChatRecordLinkView.as_view(),name='v3_share_chat'),
  path('chat/<str:chat_id>',v3_views.HistoricalConversationView.Operate.as_view(), name='v3_historical_conversation_operate'),
])),
 # ---- 全局（非 application 作用域）----
 path('embed', v3_views.ChatEmbedView.as_view()),
 path('mcp', v3_views.mcp_view),
 path('auth/anonymous', v3_views.AnonymousAuthentication.as_view()),
 path('auth/login/<str:access_token>', v3_views.LocalLoginView.as_view()),
 path('auth/logout', v3_views.Logout.as_view(), name='v3_logout'),
 path('profile', v3_views.AuthProfile.as_view()),
 path('captcha', v3_views.CaptchaView.as_view(), name='v3_captcha'),
 path('share/<str:link>', ChatRecordDetailView.as_view()),
 path('chat_message/<str:chat_id>/cancel', v3_views.CancelWorkflowView.as_view(), name='v3_cancel_workflow'),
 path('chat_user/profile', v3_views.ChatUserProfileView.as_view(), name='v3_chat_user_profile'),
 path('chat_user/current/reset_password', v3_views.ResetCurrentUserPasswordView.as_view(), name='v3_reset_password_current'),
 path('api_key', v3_views.ChatUserApiKeyView.as_view()),
 path('api_key/<int:current_page>/<int:page_size>', v3_views.ChatUserApiKeyView.Page.as_view()),
 path('api_key/<str:api_key_id>', v3_views.ChatUserApiKeyView.Operate.as_view()),
]
v2=[
    path('embed', v2_views.ChatEmbedView.as_view()),
    path('mcp', v2_views.mcp_view),
    path('auth/anonymous', v2_views.AnonymousAuthentication.as_view(), name='anonymous'),
    path('profile', v2_views.AuthProfile.as_view()),
    path('application/profile', v2_views.ApplicationProfile.as_view(), name='profile'),
    path('chat_message/<str:chat_id>', v2_views.ChatView.as_view(), name='chat'),
    path('open', v2_views.OpenView.as_view(), name='open'),
    path('text_to_speech', v2_views.TextToSpeech.as_view()),
    path('speech_to_text', v2_views.SpeechToText.as_view()),
    path('captcha', v2_views.CaptchaView.as_view(), name='captcha'),
    path('<str:application_id>/chat/completions', v2_views.OpenAIView.as_view(), name='application/chat_completions'),
    path('vote/chat/<str:chat_id>/chat_record/<str:chat_record_id>', v2_views.VoteView.as_view(), name='vote'),
    path('historical_conversation', v2_views.HistoricalConversationView.as_view(), name='historical_conversation'),
    path('historical_conversation/<str:chat_id>/record/<str:chat_record_id>',v2_views.ChatRecordView.as_view(),name='conversation_details'),
    path('historical_conversation/<int:current_page>/<int:page_size>', v2_views.HistoricalConversationView.PageView.as_view(), name='historical_conversation'),
    path('historical_conversation/clear',v2_views.HistoricalConversationView.BatchDelete.as_view(), name='historical_conversation_clear'),
    path('historical_conversation/<str:chat_id>',v2_views.HistoricalConversationView.Operate.as_view(), name='historical_conversation_operate'),
    path('historical_conversation_record/<str:chat_id>', v2_views.HistoricalConversationRecordView.as_view(), name='historical_conversation_record'),
    path('historical_conversation_record/<str:chat_id>/<int:current_page>/<int:page_size>', v2_views.HistoricalConversationRecordView.PageView.as_view(), name='historical_conversation_record'),
    path('share/<str:link>', ChatRecordDetailView.as_view()),
    path('<str:application_id>/chat/<str:chat_id>/share_chat', ChatRecordLinkView.as_view()),

]
urlpatterns = [
  *v2,
   path('v3/',include(v3))
]
