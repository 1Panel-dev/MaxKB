from django.urls import path

from . import views

app_name = "dataset"
urlpatterns = [
    path('dataset', views.Dataset.as_view(), name="dataset"),
    path('dataset/<str:dataset_id>', views.Dataset.Operate.as_view(), name="dataset_key"),
    path('dataset/<int:current_page>/<int:page_size>', views.Dataset.Page.as_view(), name="dataset"),
    path('dataset/<str:dataset_id>/document', views.Document.as_view(), name='document'),
    path('dataset/<str:dataset_id>/document/_bach', views.Document.Batch.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>', views.Document.Operate.as_view(),
         name="document_operate"),
    path('dataset/document/split', views.Document.Split.as_view(),
         name="document_operate"),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph', views.Paragraph.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<int:current_page>/<int:page_size>',
         views.Paragraph.Page.as_view(), name='paragraph_page'),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<paragraph_id>',
         views.Paragraph.Operate.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<str:paragraph_id>/problem',
         views.Problem.as_view()),
    path('dataset/<str:dataset_id>/document/<str:document_id>/paragraph/<str:paragraph_id>/problem/<str:problem_id>',
         views.Problem.Operate.as_view())
]
