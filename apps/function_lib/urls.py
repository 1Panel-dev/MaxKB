from django.urls import path

from . import views

app_name = "function_lib"
urlpatterns = [
    path('function_lib', views.FunctionLibView.as_view()),
    path('function_lib/debug', views.FunctionLibView.Debug.as_view()),
    path('function_lib/<str:function_lib_id>', views.FunctionLibView.Operate.as_view()),
    path("function_lib/<int:current_page>/<int:page_size>", views.FunctionLibView.Page.as_view(),
         name="function_lib_page"),
]
