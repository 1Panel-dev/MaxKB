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

from common.auth import TokenDetails, handles
from maxkb.const import CONFIG

content = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <script>
    function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*2));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
      window.onload = () => {
        var xhr = new XMLHttpRequest()
        xhr.open('GET', '/api/user/profile', true)

        xhr.setRequestHeader('Content-Type', 'application/json')
        const token = localStorage.getItem('token')
        const pathname = window.location.pathname
        if (token) {
          xhr.setRequestHeader('Authorization', 'Bearer '+token)
          xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                setCookie("Authorization",'Bearer '+token)
                window.location.href = pathname
              }
              if (xhr.status === 401) {
                window.location.href = '/admin/login'
              }
            }
          }

          xhr.send()
        } else {
          window.location.href = '/admin/login'
        }
      }
    </script>
  </head>
  <body></body>
</html>

""".replace("/api/user/profile", CONFIG.get_admin_path() + '/api/user/profile').replace('/admin/login',
                                                                                        CONFIG.get_admin_path() + '/login')


class DocHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/doc/') or request.path.startswith('/doc_chat/'):
            auth = request.COOKIES.get('Authorization')
            if auth is None:
                return HttpResponse(content)
            else:
                if not auth.startswith("Bearer "):
                    return HttpResponse(content)
                try:
                    token = auth[7:]
                    token_details = TokenDetails(token)
                    for handle in handles:
                        if handle.support(request, token, token_details.get_token_details):
                            handle.handle(request, token, token_details.get_token_details)
                            return response
                    return HttpResponse(content)
                except Exception as e:
                    return HttpResponse(content)
        return response
