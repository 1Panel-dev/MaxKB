from django.urls import path

from . import views

app_name = "dataset"
urlpatterns = [
    path('dataset', views.Dataset.as_view(), name="dataset"),
    path('dataset/web', views.Dataset.CreateWebDataset.as_view()),
    path('dataset/<str:dataset_id>', views.Dataset.Operate.as_view(), name="dataset_key"),
    path('dataset/<str:dataset_id>/application', views.Dataset.Application.as_view()),
    path('dataset/<int:current_page>/<int:page_size>', views.Dataset.Page.as_view(), name="dataset"),
    path('dataset/<str:dataset_id>/sync_web', views.Dataset.SyncWeb.as_view()),
    path('dataset/<str:dataset_id>/hit_test', views.Dataset.HitTest.as_view()),
    path('dataset/<str:dataset_id>/document', views.Document.as_view(), name='document'),
    path('dataset/<str:dataset_id>/document/web', views.WebDocument.as_view()),
    path('dataset/<str:dataset_id>/document/_bach', views.Document.Batch.as_view()),
    path('dataset/<str:dataset_id>/document/<int:current_page>/<int:page_size>', views.Document.Page.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>', views.Document.Operate.as_view(),
         name="document_operate"),
    path('dataset/document/split', views.Document.Split.as_view(),
         name="document_operate"),
    path('dataset/document/split_pattern', views.Document.SplitPattern.as_view(),
         name="document_operate"),
    path('dataset/<str:dataset_id>/document/<str:document_id>/refresh', views.Document.Refresh.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph', views.Paragraph.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<int:current_page>/<int:page_size>',
         views.Paragraph.Page.as_view(), name='paragraph_page'),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<paragraph_id>',
         views.Paragraph.Operate.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<str:paragraph_id>/problem',
         views.Paragraph.Problem.as_view()),
    path(
        'dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<str:paragraph_id>/problem/<str:problem_id>/un_association',
        views.Paragraph.Problem.UnAssociation.as_view()),
    path(
        'dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<str:paragraph_id>/problem/<str:problem_id>/association',
        views.Paragraph.Problem.Association.as_view()),
    path('dataset/<str:dataset_id>/problem', views.Problem.as_view()),
    path('dataset/<str:dataset_id>/problem/_batch', views.Problem.OperateBatch.as_view()),
    path('dataset/<str:dataset_id>/problem/<int:current_page>/<int:page_size>', views.Problem.Page.as_view()),
    path('dataset/<str:dataset_id>/problem/<str:problem_id>', views.Problem.Operate.as_view()),
    path('dataset/<str:dataset_id>/problem/<str:problem_id>/paragraph', views.Problem.Paragraph.as_view()),

]
