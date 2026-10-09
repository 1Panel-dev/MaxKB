# Chat API

`core/request.ts` 提供独立的 Axios 客户端、JSON 响应解包和 `postStream` 流式请求，
不复用 Admin 请求客户端。JSON 与流式请求通过 `@/stores/chat` 的 `useStore()` 获取当前认证场景
（门户或单应用）的 token 和语言。
401 响应（`/auth/` 认证接口除外）不弹出通用提示，调用 `@/router/chat` 的 `reauthenticate()` 重新认证。
流式请求返回原始 `Response`，由对话面板解析，不在请求层维护消息或 loading。

`conversation.ts` 维护正式对话的打开、发送、取消、续传、历史分页、记录分页、删除、修改、
语音识别接口，默认导出完整 API 对象。调试对话接口位于
`admin/workspace/conversation.ts`，面板模式选择位于 `conversation-panel/common/get-api.ts`。

Chat 业务接口统一调用后端 v3 路由（`/chat/api/v3/...`）；文件上传 `/oss/file` 由 oss 模块提供，不在 v3 下。
通用错误提示使用响应的 `message`；响应为 HTML 时按 HTTP 状态显示通用文案。

接口命名、类型和请求约定统一遵循 `../API_README.md`。

`file.ts` 提供通用 `postUploadFile`，通过本应用的 `core/request.ts` 中 `postUpload` 支持
可选进度回调及取消，统一返回 `{ request, abort }`。`request` 解包得到文件地址；
取消仍拒绝 Promise，但不弹出通用错误提示。loading 由调用方管理。

`auth.ts` 维护门户与单应用的认证：`getApplicationAuthProfile(accessToken)` 请求 `/profile`，
`getPortalAuthProfile()` 请求 `/portal/profile`，两者返回结构相同的 `AuthProfile`，差异字段在 `meta`。
`postAnonymousAuth(accessToken?)` 与 `postLogin(loginRequest, accessToken?)` 传入 accessToken 时为应用认证，
否则为门户认证。`getCaptcha(username, accessToken)` 获取应用登录验证码，后端目前以 `application_id`
查询参数接收 accessToken，暂不支持门户。`chat-user.ts` 的 `getChatUserProfile()` 获取当前对话用户。
