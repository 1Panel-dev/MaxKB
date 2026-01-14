# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： urls.py
    @date：2026/1/9 16:15
    @desc:
"""
from django.urls import path

from . import views

app_name = "trigger"

urlpatterns = [
    path('workspace/<str:workspace_id>/trigger', views.TriggerView.as_view(), name='trigger'),
    path('workspace/<str:workspace_id>/trigger/<int:current_page>/<int:page_size>', views.TriggerView.Page.as_view(),
         name='trigger_page'),
    path('workspace/<str:workspace_id>/task', views.TriggerTaskView.as_view(), name='task'),
]
