from django.urls import path

from . import views

app_name = "knowledge"
urlpatterns = [
    path('workspace/<str:workspace_id>/knowledge', views.KnowledgeView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/base', views.KnowledgeBaseView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/web', views.KnowledgeWebView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>', views.KnowledgeView.Operate.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document', views.DocumentView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/split', views.DocumentView.Split.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/batch', views.DocumentView.Batch.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/web', views.WebDocumentView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/qa', views.QaDocumentView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/table', views.TableDocumentView.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/batch_hit_handling', views.DocumentView.BatchEditHitHandling.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/<str:document_id>', views.DocumentView.Operate.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/<str:document_id>/sync', views.DocumentView.SyncWeb.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/<str:document_id>/refresh', views.DocumentView.Refresh.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/<str:document_id>/cancel_task', views.DocumentView.CancelTask.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<str:knowledge_id>/document/<str:document_id>/cancel_task/batch', views.DocumentView.BatchCancelTask.as_view()),
    path('workspace/<str:workspace_id>/knowledge/<int:current_page>/<int:page_size>', views.KnowledgeView.Page.as_view()),
]
