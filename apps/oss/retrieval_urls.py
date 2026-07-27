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
    re_path(r'^(.*)/oss/file/(?P<file_id>[\w-]+)/?$',
            views.FileRetrievalView.as_view()),
    re_path(r'oss/file/(?P<file_id>[\w-]+)/?$',
            views.FileRetrievalView.as_view()),
    re_path(r'^oss/get_url/(?P<application_id>[\w-]+)/?$',
            views.GetUrlView.as_view()),

]
