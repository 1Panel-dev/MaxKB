import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from chat.mcp.tools import MCPToolHandler


@csrf_exempt
def mcp_view(request):
    request_id = None
    try:
        data = json.loads(request.body)
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")

        if request_id is None:
            return HttpResponse(status=204)

        auth_header = request.headers.get("Authorization", "").replace("Bearer ", "")
        handler = MCPToolHandler(auth_header)

        # 路由方法
        if method == "initialize":
            result = handler.initialize()

        elif method == "tools/list":
            result = handler.list_tools()

        elif method == "tools/call":
            result = handler.call_tool(params)

        else:
            return JsonResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })

        # 成功响应
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        })

    except Exception as e:
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        })
