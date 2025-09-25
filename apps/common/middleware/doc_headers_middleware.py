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
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
  </head>
  <style>
    /* 弹框内容样式 */
    .modal-content {
      background-color: #fefefe;
      margin: 15% auto; /* 15% 从顶部和自动水平居中 */
      padding: 20px;
      border: 1px solid #888;
      width: 80%; /* 宽度 */
    }
  </style>
  <body>
    <div class="modal-content">
      <input type="text" id="auth-input" />
      <button id="auth">认证</button>
      <button id="goLogin">去登录</button>
    </div>
    <script>
      const setCookie = (name, value, days) => {
        var expires = "";
        if (days) {
          var date = new Date();
          date.setTime(date.getTime() + days * 2);
          expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
      };
      const authToken = (token) => {
        return new Promise((resolve, reject) => {
          try {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/api/user/profile", true);
            xhr.setRequestHeader("Content-Type", "application/json");
            const pathname = window.location.pathname;
            if (token) {
              xhr.setRequestHeader("Authorization", "Bearer " + token);
              xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                  if (xhr.status === 200) {
                    resolve(true);
                  } else {
                    reject(true);
                  }
                }
              };

              xhr.send();
            }
          } catch (e) {
            reject(false);
          }
        });
      };
      window.onload = () => {
        const token = localStorage.getItem("token");
        authToken(token)
          .then(() => {
            setCookie("Authorization", "Bearer " + token);
            window.location.href = window.location.pathname;
          })
          .catch((e) => {});
      };
      // 获取元素
      const auth = document.getElementById("auth");
      const goLogin = document.getElementById("goLogin");

      // 打开弹框函数
      auth.onclick = ()=> {
        const authInput = document.getElementById("auth-input");
        const token = authInput.value
        authToken(token)
          .then(() => {
            setCookie("Authorization", "Bearer " + token);
            window.location.href = window.location.pathname;
          })
          .catch((e) => {
            alert("令牌错误");
          });
      };

      // 去系统的登录页面
      goLogin.onclick =  ()=> {
        window.location.href = "/admin/login";
      };
    </script>
  </body>
</html>

""".replace("/api/user/profile", CONFIG.get_admin_path() + '/api/user/profile').replace('/admin/login',
                                                                                        CONFIG.get_admin_path() + '/login')


class DocHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith(CONFIG.get_admin_path() + '/api-doc/') or request.path.startswith(
                CONFIG.get_chat_path() + '/api-doc/'):
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
