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
from .handler.impl.trigger.event_trigger import EventTriggerView

app_name = "trigger"

urlpatterns = [
    path('workspace/<str:workspace_id>/trigger', views.TriggerView.as_view(), name='trigger'),
    path('workspace/<str:workspace_id>/trigger/batch_delete', views.TriggerView.BatchDelete.as_view(),
         name='delete batch'),
    path('workspace/<str:workspace_id>/trigger/batch_activate', views.TriggerView.BatchActivate.as_view(),
         name='activate batch'),
    path('workspace/<str:workspace_id>/trigger/<str:trigger_id>', views.TriggerView.Operate.as_view(),
         name='trigger operate'),
    path('workspace/<str:workspace_id>/trigger/<int:current_page>/<int:page_size>', views.TriggerView.Page.as_view(),
         name='trigger_page'),
    path('workspace/<str:workspace_id>/<str:source_type>/<str:source_id>/trigger/<str:trigger_id>',
         views.TaskSourceTriggerView.Operate.as_view(), name='task source trigger operate'),
    path('workspace/<str:workspace_id>/<str:source_type>/<str:source_id>/trigger',
         views.TaskSourceTriggerView.as_view(), name='task source trigger'),
    path(
        'workspace/<str:workspace_id>/trigger/<str:trigger_id>/task_record/<int:current_page>/<int:page_size>',
        views.TriggerTaskRecordPageView.as_view(), name='trigger_task_record'),
    path('workspace/<str:workspace_id>/task', views.TriggerTaskView.as_view(), name='task'),
    path('trigger/v1/webhook/<str:trigger_id>', EventTriggerView.as_view(), name='trigger_webhook'),
    path(
        'workspace/<str:workspace_id>/trigger/<str:trigger_id>/trigger_task/<str:trigger_task_id>/trigger_task_record/<str:trigger_task_record_id>',
        views.TriggerTaskRecordExecutionDetailsView.as_view(), name='task source trigger'),
]
