from django.urls import path

from . import views

app_name = "module"
urlpatterns = [
    path('workspace/<str:workspace_id>/<str:source>/module', views.ModuleView.Create.as_view()),
    path('workspace/<str:workspace_id>/<str:source>/module', views.ModuleTreeView.as_view()),
    path('workspace/<str:workspace_id>/<str:source>/module/<str:module_id>', views.ModuleView.Operate.as_view()),
]
