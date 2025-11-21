# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： retrieval_urls.py
    @date：2025/7/2 19:01
    @desc:
"""
from django.urls import re_path

from . import views

app_name = 'oss'

urlpatterns = [
    re_path(rf'^(.*)/oss/file/(?P<file_id>[\w-]+)/?$',
            views.FileRetrievalView.as_view()),
    re_path(rf'oss/file/(?P<file_id>[\w-]+)/?$',
            views.FileRetrievalView.as_view()),
    re_path(rf'^/oss/get_url/(?P<url>[\w-]+)?$',
            views.GetUrlView.as_view()),

]
