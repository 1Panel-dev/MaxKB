# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： cross_domain_middleware.py
    @date：2024/5/8 13:36
    @desc:
"""
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from common.cache_data.application_api_key_cache import get_application_api_key


class CrossDomainMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.method == 'OPTIONS':
            return HttpResponse(status=200,
                                headers={
                                    "Access-Control-Allow-Origin": "*",
                                    "Access-Control-Allow-Methods": "GET,POST,DELETE,PUT",
                                    "Access-Control-Allow-Headers": "Origin,X-Requested-With,Content-Type,Accept,Authorization,token"})

    def process_response(self, request, response):
        auth = request.META.get('HTTP_AUTHORIZATION')
        origin = request.META.get('HTTP_ORIGIN')
        if auth is not None and str(auth).startswith("application-") and origin is not None:
            application_api_key = get_application_api_key(str(auth), True)
            cross_domain_list = application_api_key.get('cross_domain_list', [])
            allow_cross_domain = application_api_key.get('allow_cross_domain', False)
            if allow_cross_domain:
                response['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PUT'
                response[
                    'Access-Control-Allow-Headers'] = "Origin,X-Requested-With,Content-Type,Accept,Authorization,token"
                if cross_domain_list is None or len(cross_domain_list) == 0:
                    response['Access-Control-Allow-Origin'] = "*"
                elif cross_domain_list.__contains__(origin):
                    response['Access-Control-Allow-Origin'] = origin
        return response
