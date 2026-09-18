# Chat API

`core/request.ts` 提供独立的 Axios 客户端、JSON 响应解包和 `postStream` 流式请求，
不复用 Admin 请求客户端。当前 JSON 与流式请求均通过 `useStore()` 获取已有 token 和语言。
流式请求返回原始 `Response`，由对话面板解析，不在请求层维护消息或 loading。

`conversation.ts` 维护正式对话的打开、发送、取消、续传、历史分页、记录分页、删除、修改、
语音识别接口，默认导出完整 API 对象。调试对话接口位于
`admin/workspace/conversation.ts`，面板模式选择位于 `conversation-panel/common/get-api.ts`。

接口命名、类型和请求约定统一遵循 `../API_README.md`。

`file.ts` 提供通用 `postUploadFile`，通过本应用的 `core/request.ts` 中 `postUpload` 支持
可选进度回调及取消，统一返回 `{ request, abort }`。`request` 解包得到文件地址；
取消仍拒绝 Promise，但不弹出通用错误提示。loading 由调用方管理。
