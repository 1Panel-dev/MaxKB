# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： static_headers_middleware.py
    @date：2024/3/13 18:26
    @desc:
"""
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

content = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <script>
      window.onload = () => {
        var xhr = new XMLHttpRequest()
        xhr.open('GET', '/api/user', true)

        xhr.setRequestHeader('Content-Type', 'application/json')
        const token = localStorage.getItem('token')
        const pathname = window.location.pathname
        if (token) {
          xhr.setRequestHeader('Authorization', token)
          xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                window.location.href = pathname
              }
              if (xhr.status === 401) {
                window.location.href = '/ui/login'
              }
            }
          }

          xhr.send()
        } else {
          window.location.href = '/ui/login'
        }
      }
    </script>
  </head>
  <body></body>
</html>

"""


class DocHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/doc/') or request.path.startswith('/doc/chat/'):
            HTTP_REFERER = request.META.get('HTTP_REFERER')
            if HTTP_REFERER is None:
                return HttpResponse(content)
            if HTTP_REFERER == request._current_scheme_host + request.path:
                return response
        return response
