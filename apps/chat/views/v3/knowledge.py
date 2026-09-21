"""Public knowledge API/MCP endpoints, following the existing application MCP endpoint."""

import json
from urllib.parse import urlsplit

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.exceptions import ValidationError

from chat.mcp.knowledge import KnowledgeMCPToolHandler, PROTOCOL_VERSIONS
from knowledge.services.external_retrieval import retrieve
from knowledge.services.retrieval_access import RetrievalError, authenticate_key, authorize_external


def response_headers(response):
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    if response.status_code == 401:
        response["WWW-Authenticate"] = "Bearer"
    return response


def read_request(request, knowledge_id):
    origin = request.headers.get("Origin")
    if origin:
        expected = urlsplit(request.build_absolute_uri("/"))
        if origin != f"{expected.scheme}://{expected.netloc}":
            raise RetrievalError("invalid_origin", "Origin is not allowed.", 403)
    identity = authenticate_key(request.headers.get("Authorization"))
    knowledge = authorize_external(knowledge_id, identity)
    if request.content_type != "application/json":
        raise RetrievalError("invalid_content_type", "Use application/json.", 415)
    if int(request.META.get("CONTENT_LENGTH") or 0) > 65536:
        raise RetrievalError("request_too_large", "Request body is too large.", 413)
    body = request.body
    if len(body) > 65536:
        raise RetrievalError("request_too_large", "Request body is too large.", 413)
    return knowledge, identity, json.loads(body)


def error_response(error):
    return response_headers(
        JsonResponse({"error": {"code": error.code, "message": error.message}}, status=error.status)
    )


@csrf_exempt
@require_POST
def retrieve_view(request, knowledge_id):
    try:
        knowledge, identity, data = read_request(request, knowledge_id)
        return response_headers(JsonResponse(retrieve(knowledge.id, identity, data)))
    except RetrievalError as error:
        return error_response(error)
    except (ValueError, UnicodeError, ValidationError):
        return error_response(RetrievalError("invalid_request", "Invalid retrieval request."))
    except Exception:
        return error_response(RetrievalError("retrieval_failed", "Knowledge retrieval failed.", 503))


def rpc_response(request_id, result=None, code=None, message=None, status=200):
    data = {"jsonrpc": "2.0", "id": request_id}
    data.update({"error": {"code": code, "message": message}} if code is not None else {"result": result})
    return response_headers(JsonResponse(data, status=status))


@csrf_exempt
@require_POST
def knowledge_mcp_view(request, knowledge_id):
    request_id = None
    try:
        knowledge, identity, data = read_request(request, knowledge_id)
        accept = request.headers.get("Accept", "")
        if not all(value in accept for value in ("application/json", "text/event-stream")):
            return rpc_response(
                None, code=-32600, message="Accept must include application/json and text/event-stream.", status=406
            )
        if request.headers.get("MCP-Protocol-Version", "2025-03-26") not in PROTOCOL_VERSIONS:
            return rpc_response(None, code=-32600, message="Unsupported protocol version.", status=400)
        if not isinstance(data, dict) or data.get("jsonrpc") != "2.0" or not isinstance(data.get("method"), str):
            return rpc_response(None, code=-32600, message="Invalid Request")
        request_id = data.get("id")
        if "id" in data and (isinstance(request_id, bool) or not isinstance(request_id, (str, int))):
            return rpc_response(None, code=-32600, message="Invalid request ID.")
        params = data.get("params", {})
        if not isinstance(params, dict):
            return (
                rpc_response(request_id, code=-32602, message="Invalid params.")
                if "id" in data
                else HttpResponse(status=400)
            )
        if "id" not in data:
            return response_headers(HttpResponse(status=202))
        handler = KnowledgeMCPToolHandler(knowledge, identity)
        method = data["method"]
        if method == "initialize":
            output = handler.initialize(params)
        elif method == "ping":
            output = {}
        elif method == "tools/list":
            output = handler.list_tools()
        elif method == "tools/call":
            output = handler.call_tool(params)
        else:
            return rpc_response(request_id, code=-32601, message="Method not found.")
        return rpc_response(request_id, result=output)
    except RetrievalError as error:
        return error_response(error)
    except (ValueError, UnicodeError):
        return rpc_response(None, code=-32700, message="Parse error.", status=400)
    except ValidationError:
        return rpc_response(request_id, code=-32602, message="Invalid params.")
    except Exception:
        return rpc_response(request_id, code=-32603, message="Knowledge retrieval failed.", status=503)
