# 知识库外部检索服务

本次仅实现后端配置与检索接口，供「知识库 → 授权与集成 → 外部检索服务」页面接入。
MCP 沿用智能体的 Django HTTP 入口与 ToolHandler 结构，
支持 Streamable HTTP 的 JSON 响应；不新增服务进程、队列或生产依赖，不改动 ChatUserApiKey。

## 配置与兼容

`Knowledge.external_service` 保存两个开关：`enabled`（外部 API/MCP）和 `authentication`（身份认证）。
新知识库的外部服务和身份认证均默认关闭：`enabled=false, authentication=false`。迁移 `0015_knowledge_external_service`
给旧库写入空配置：外部服务关闭，内部检索继续原有规则；管理员显式修改身份认证后采用新开关规则。
只切换外部服务不会改变旧库内部鉴权。迁移需按项目部署流程执行，开发时不自动应用。

管理接口为 `GET/PUT /admin/api/workspace/{workspace_id}/knowledge/{knowledge_id}/external_service`，
使用现有管理员 Token 和知识库读/编辑权限。PUT 只提交本次修改的开关，例如 `{"enabled":true}`；
其他配置保留。响应中的地址使用当前部署前缀，MCP 配置仅包含 Key 占位符。

外部服务关闭时，两种入口都返回 404。身份认证开启时，需要有效且启用的对话用户 API Key、
启用的用户和现有用户/用户组知识库授权；关闭时允许匿名。显式传入无效 Key 返回 401。
Key 创建、查询、删除仍用原有 `/chat/api/v3/api_key` 接口。检索期间再次检查撤权及服务关闭。

身份认证开关同样覆盖应用内知识库检索、文档检索和工具工作流。身份取自后端认证结果，
不使用 `form_data.asker`，子工具参数不能覆盖它。管理员调试仍检查后台资源权限。
外部服务开关不影响内部检索。

## REST

`POST /chat/api/v3/knowledge/{knowledge_id}/retrieve`

```bash
curl "$BASE_URL/chat/api/v3/knowledge/$KNOWLEDGE_ID/retrieve" \
  -H "Authorization: Bearer $CHAT_USER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"query_text":"如何使用知识库？","top_number":5,"similarity":0,"search_mode":"embedding"}'
```

身份认证关闭时可省略 Authorization。文本最长 8000 字符，top_number 为 1–50（默认 5），
similarity 为 0–1（默认 0），search_mode 支持 embedding、keywords、blend（默认 embedding）。
检索限定当前知识库，返回 `knowledge_id` 和 `hits`，命中包含段落正文（最多 8000 字符）、
分数、来源与 `citation`（知识库、文档、段落 ID 和名称）；不生成回答。
过滤跨库、停用或失效段落，仅对实际返回命中累计原有召回统计。正文中的附件沿用现有文件访问规则。

请求体最大 64 KiB。400 为参数错误、401 为缺少/无效凭据、403 为无权限/不允许的 Origin、
404 为服务不可用、413 为请求超限、415 为媒体类型错误、503 为检索依赖失败。
错误不会返回内部异常或模型凭据。响应设置 `Cache-Control: no-store`。

## MCP

`POST /chat/api/v3/knowledge/{knowledge_id}/mcp`，与智能体 `/chat/api/v3/mcp` 并存。
工具名为 `knowledge_{knowledge_id}`，输入与 REST 相同，返回文本 content 内的同一份 JSON 结果。
配置接口返回的 `mcp_config` 可直接用于 MaxKB 的 MCP 工具配置，认证开启时替换 Key 占位符。

```json
{
  "knowledge_example": {
    "url": "https://example.com/chat/api/v3/knowledge/KNOWLEDGE_ID/mcp",
    "transport": "streamable_http",
    "headers": {"Authorization": "Bearer <CHAT_USER_API_KEY>"}
  }
}
```

遵循 [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)：
客户端发送 `Accept: application/json, text/event-stream`、`Content-Type: application/json`；
初始化后携带协商的 `MCP-Protocol-Version`。支持 2025-03-26、2025-06-18、2025-11-25，
提供 initialize、ping、tools/list、tools/call；通知返回 202，不执行工具。不建立持久会话，
GET/DELETE 返回 405。不提供旧 SSE 或 OAuth 自动发现。带 Origin 的请求须与当前服务同源。

## 验证

`python apps/manage.py test knowledge.test_external_retrieval` 包含两开关规则、旧库兼容、
原有 Key、授权撤销、跨库过滤、管理员调试、JSON-RPC 和真实 MCP Python SDK 的内存 HTTP 往返测试。
真实 PostgreSQL/pgvector、模型供应商和外部客户端仍需在配置好的测试环境完成部署验收。
