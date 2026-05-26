from django.urls import path

from . import views

app_name = "homepage"
# @formatter:off
# fmt: off

urlpatterns = [
    path("workspace/<str:workspace_id>/homepage/application/aggregation",views.HomePageAPI.ApplicationAggregation.as_view()),
    path("workspace/<str:workspace_id>/homepage/application/tokens_ranking/<int:current_page>/<int:page_size>",views.HomePageAPI.ApplicationTokensRanking.as_view()),
    path("workspace/<str:workspace_id>/homepage/application/question_ranking/<int:current_page>/<int:page_size>",views.HomePageAPI.ApplicationQuestionRanking.as_view()),
    path("workspace/<str:workspace_id>/homepage/application/user_tokens_ranking/<int:current_page>/<int:page_size>",views.HomePageAPI.UserTokensRanking.as_view()),
    path("workspace/<str:workspace_id>/homepage/monitoring/aggregation",views.HomePageAPI.ApplicationMonitoring.as_view()),
    path("workspace/<str:workspace_id>/homepage/knowledge/aggregation",views.HomePageAPI.KnowledgeAggregation.as_view()),
    path("workspace/<str:workspace_id>/homepage/tool/aggregation",views.HomePageAPI.ToolAggregation.as_view()),
    path("workspace/<str:workspace_id>/homepage/model/aggregation",views.HomePageAPI.ModelAggregation.as_view()),
    path("workspace/<str:workspace_id>/homepage/tokens/aggregation",views.HomePageAPI.TokensAggregation.as_view()),
    path("workspace/<str:workspace_id>/homepage/chat_record/aggregation",views.HomePageAPI.ChatRecordAggregation.as_view()),
    path("workspace/<str:workspace_id>/homepage/question_ranking/export",views.HomePageAPI.ApplicationQuestionRankingExport.as_view()),
    path("workspace/<str:workspace_id>/homepage/tokens_ranking/export",views.HomePageAPI.ApplicationTokensRankingExport.as_view()),
    path("workspace/<str:workspace_id>/homepage/user_tokens_ranking/export",views.HomePageAPI.UserTokensRankingExport.as_view())
]
