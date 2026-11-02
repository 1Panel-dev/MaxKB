import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from chat.mcp.tools import ChatUserMCPToolHandler, InvalidParamsError
from common.auth.handle.impl.chat_user_key import ChatUserKey
from common.exception.app_exception import AppAuthenticationFailed


def rpc_response(request_id, result=None, code=None, message=None, status=200):
    data = {"jsonrpc": "2.0", "id": request_id}
    data.update({"error": {"code": code, "message": message}} if code is not None else {"result": result})
    response = JsonResponse(data, status=status)
    if status == 401:
        response["WWW-Authenticate"] = "Bearer"
    return response


def authenticate(request, application_id=None):
    """
    MCP 接口使用对话用户 API Key（chat-xxx）认证；带 application_id 时只暴露该应用
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    chat_user_key = ChatUserKey()
    if not chat_user_key.support(request, token, None):
        raise AppAuthenticationFailed(1002, "Chat user API key is required")
    principal, auth = chat_user_key.handle(request, token, None)
    return ChatUserMCPToolHandler(principal.profile, auth, application_id)


@csrf_exempt
@require_POST
def mcp_view(request, application_id=None):
    request_id = None
    try:
        handler = authenticate(request, application_id)
        data = json.loads(request.body)
        if not isinstance(data, dict) or not isinstance(data.get("method"), str):
            return rpc_response(None, code=-32600, message="Invalid Request")
        method = data.get("method")
        params = data.get("params") or {}
        request_id = data.get("id")

        # 通知消息无需响应
        if request_id is None:
            return HttpResponse(status=202)

        # 路由方法
        if method == "initialize":
            result = handler.initialize()

        elif method == "ping":
            result = {}

        elif method == "tools/list":
            result = handler.list_tools()

        elif method == "tools/call":
            result = handler.call_tool(params)

        else:
            return rpc_response(request_id, code=-32601, message=f"Method not found: {method}")

        # 成功响应
        return rpc_response(request_id, result=result)

    except AppAuthenticationFailed as e:
        return rpc_response(request_id, code=-32001, message=str(e.message), status=401)
    except InvalidParamsError as e:
        return rpc_response(request_id, code=-32602, message=str(e))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return rpc_response(None, code=-32700, message="Parse error", status=400)
    except Exception as e:
        return rpc_response(request_id, code=-32603, message=f"Internal error: {str(e)}")
