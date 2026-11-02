import json
import queue
import threading

from django.db import connection
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
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


# 智能体执行期间推送进度/心跳的间隔（秒），保证客户端读超时不会在长任务中触发
SSE_HEARTBEAT_SECONDS = 15


def rpc_error(error):
    if isinstance(error, InvalidParamsError):
        return -32602, str(error)
    return -32603, f"Internal error: {str(error)}"


def sse_event(data):
    return f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def stream_tool_call(handler, params, request_id):
    """
    tools/call 以 SSE 返回：后台线程执行智能体，期间定时推送进度通知（客户端带 progressToken 时）或心跳注释，
    结束后推送 JSON-RPC 结果。长任务不会因为长时间收不到数据而触发客户端 ReadTimeout。
    """
    result_queue = queue.Queue()

    def run():
        try:
            result_queue.put(("result", handler.call_tool(params)))
        except Exception as e:
            result_queue.put(("error", e))
        finally:
            connection.close()

    threading.Thread(target=run, daemon=True).start()
    progress_token = (params.get("_meta") or {}).get("progressToken")
    progress = 0
    while True:
        try:
            kind, value = result_queue.get(timeout=SSE_HEARTBEAT_SECONDS)
        except queue.Empty:
            progress += 1
            if progress_token is None:
                yield ": ping\n\n"
            else:
                yield sse_event(
                    {
                        "jsonrpc": "2.0",
                        "method": "notifications/progress",
                        "params": {
                            "progressToken": progress_token,
                            "progress": progress,
                            "message": "Agent is working",
                        },
                    }
                )
            continue
        if kind == "result":
            yield sse_event({"jsonrpc": "2.0", "id": request_id, "result": value})
        else:
            code, message = rpc_error(value)
            yield sse_event({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})
        return


def sse_response(stream):
    response = StreamingHttpResponse(stream, content_type="text/event-stream; charset=utf-8")
    response["Cache-Control"] = "no-cache"
    # 关闭 Nginx 等反向代理的缓冲，心跳才能及时到达客户端
    response["X-Accel-Buffering"] = "no"
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
            # 智能体执行可能长达数分钟，客户端支持 SSE 时流式返回
            if "text/event-stream" in request.headers.get("Accept", ""):
                return sse_response(stream_tool_call(handler, params, request_id))
            result = handler.call_tool(params)

        else:
            return rpc_response(request_id, code=-32601, message=f"Method not found: {method}")

        # 成功响应
        return rpc_response(request_id, result=result)

    except AppAuthenticationFailed as e:
        return rpc_response(request_id, code=-32001, message=str(e.message), status=401)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return rpc_response(None, code=-32700, message="Parse error", status=400)
    except Exception as e:
        code, message = rpc_error(e)
        return rpc_response(request_id, code=code, message=message)
