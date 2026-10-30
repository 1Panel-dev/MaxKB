# 工作流测试

## Excel 文档分段

从集成仓库根目录运行：

```bash
uv run python apps/manage.py test application.tests.test_workflow_excel_split \
  application.tests.test_workflow_document_source
```

Excel 的智能、自定义和 QA 分段均按 sheet 输出独立文档。测试使用内存中的 XLSX、XLS
文件经过真实提取、分段节点，覆盖 sheet 命名、原文件及来源元数据、分段长度、QA 问题
和非 Excel 文档兼容性。文件查询使用替身，不验证数据库入库或前端显示。

## 工作流 Web 图片导入

工作流 Web 图片导入的 HTTP 回归使用 Postman CLI 1.70 或更高版本：

```bash
postman simulation run apps/application/tests/fixtures/workflow_web_images.sim.yaml --port 49643 --no-history
```

另一个终端运行：

```bash
WORKFLOW_WEB_IMAGE_TEST_URL=http://127.0.0.1:49643 \
  uv run python apps/manage.py test application.tests.test_workflow_web_images
```

测试通过真实网页抓取执行器和 boto3 客户端访问本地网页、图片和 S3 对象存储模拟，
覆盖抓取、图片下载、保存、分段、文档写入及段落附件关联。重复导入复用已保存的图片；
下载失败保留原链接，正文仍可导入。测试数据为合成内容，不调用模型。

网页模拟提供普通 HTTP GET；对象存储模拟仅覆盖 S3 PutObject、GetObject 和 DeleteObject，
不验证真实站点的访问权限、重定向或远端存储服务。未设置环境变量时跳过两项 HTTP 回归，
其余工作流图片测试照常运行。

## LangChain 流式输出、工具调用与 token 统计

纯消息处理、usage 优先级、取消处理和已有工具展示回归不依赖外部服务：

```bash
uv run python apps/manage.py test application.tests.test_langchain_compatibility \
  application.tests.test_ai_chat_tool_output
```

HTTP 回归使用 Postman CLI 1.74.0 验证过的本地模拟，复用已有 DeepSeek 工具图片模拟：

```bash
postman simulation run apps/application/tests/fixtures/langchain-compatibility.sim.yaml \
  --port 49645 --no-history --output ndjson
```

另一个终端从集成仓库根目录运行：

```bash
LANGCHAIN_COMPAT_TEST_URL=http://127.0.0.1:49645/provider \
DEEPSEEK_TOOL_IMAGE_TEST_URL=http://127.0.0.1:49645/deepseek/v1 \
  uv run python apps/manage.py test application.tests.test_langchain_compatibility \
  application.tests.test_ai_chat_tool_output models_provider.tests.test_deepseek_tool_images
```

覆盖真实 OpenAI / Anthropic SDK 的同步和异步响应解析、中文/推理内容分片、Qwen 空 ID
工具参数合并、交错工具调用、流末尾 usage、缓存 token，以及 429 异常传播。
Agent 用例运行真实 deepagents / LangGraph 和两个本地工具调用，验证调用 ID、参数、工具结果
及下一轮回答；MCP 工具发现和技能加载被替换，未验证远端 MCP 传输或 Linux 沙箱隔离。
每个 HTTP 用例独立管理连接池和事件循环，避免把跨测试复用已关闭事件循环误判为 SDK 回归。

统计沿用现有行为：OpenAI 的缓存/推理 token 是输入/输出总量的细分，不重复累加；Anthropic
输入总量包括非缓存、缓存读取和缓存写入 token，模拟在最终 `message_delta` 返回累计 usage。
当前 Anthropic 适配器依赖此最终 usage；只在 `message_start` 返回输入用量的兼容网关不在
本次通过的场景内。Agent 模型适配器记录最后一轮用量，未改为所有工具轮次的总和。

本次仅验证虚拟密钥和合成响应下的协议兼容性，不验证真实云模型效果或真实账单。
未设置环境变量时 HTTP 用例会跳过。模拟依据、运行结果和限制记录在
`fixtures/langchain-compatibility.context.yaml`；使用 Ctrl-C 停止模拟服务。

### 完整升级与 Bedrock 回归（2026-10-29）

根、community、xpack 三份依赖配置同步使用 deepagents 0.7.32、langchain-core 1.7.1、
langchain-openai 1.7.3、langchain-aws 1.9.1 和 langgraph 1.2.18。
当时上述命令运行 45 项定向测试；原有 33 项在升级前后都通过。

新增 Bedrock 用例使用真实 boto3 客户端和适配器，覆盖 InvokeModel、带 CRC 的二进制
InvokeModelWithResponseStream、中文工具参数与结果回传、视觉图片请求和 429 错误传播。
LLM 节点的输入总量包含普通输入、缓存读取和缓存写入各一次：模拟的 10 + 3 + 2 个输入
token 加 4 个输出 token，共计 19。这遵循 langchain-aws 1.9 的缓存计数修正；有缓存的
请求相较旧版本可能显示更高的输入总量，测试不代表真实账单。

补测修复了两个已有兼容缺口：`astream()` 回退完整 `AIMessage` 时，LLM 节点会复制转换
为分片再处理工具参数；模型返回列表内容块时，LLM 与 Agent 从中提取文本用于答案展示，
工具/推理等原始块保留在消息历史中。回归验证文本、工具卡片、usage 和原始消息不被改写。
还覆盖 Agent 递归上限的错误传播与工作目录清理，以及 Shell 后端的 UTF-8 字节截断、
虚拟技能路径和退出码。Shell 测试临时关闭 Linux 隔离包装，只在临时目录执行合成命令。

扩展回归复用模型提供商 README 中的 multimodal（49643）与 vllm-rerank（49646）模拟，
与此处 LangChain 模拟一起启动后运行：

```bash
LANGCHAIN_COMPAT_TEST_URL=http://127.0.0.1:49645/provider \
DEEPSEEK_TOOL_IMAGE_TEST_URL=http://127.0.0.1:49645/deepseek/v1 \
MULTIMODAL_EMBEDDING_TEST_URL=http://127.0.0.1:49643 \
ALIYUN_EMBEDDING_TEST_URL=http://127.0.0.1:49643/aliyun/api/v1 \
SILICONFLOW_EMBEDDING_TEST_URL=http://127.0.0.1:49643/siliconflow/v1 \
VLLM_RERANK_TEST_URL=http://127.0.0.1:49646/vllm \
  uv run python apps/manage.py test application.tests.test_langchain_compatibility \
  application.tests.test_ai_chat_tool_output application.tests.test_workflow_nodes \
  models_provider.tests --noinput
```

本次 117 项扩展回归全部通过，无跳过；这些 SimpleTestCase 不验证数据库持久化。

### Bedrock 完整消息兼容修复（2026-10-30）

低风险依赖升级后的检查发现当前代码有两项已有失败：测试调用 `_write_final_context`
未传新增的 `reasoning_key`；LLM 节点把非流式回退的完整 `AIMessage` 当作分片，访问
`tool_call_chunks` 时抛错。boto3/botocore 1.43.121 和 1.43.122 均复现相同失败。

现已补齐四处测试调用的关键字参数，并恢复完整消息的副本转换及文本块提取，保留当前
`reasoning_key` 和思考结束事件处理。新增回归覆盖字符串/列表内容、两个工具调用及显示 ID、
思考字段、usage、结束原因、原始消息不变和流关闭。

使用上面的 LangChain 模拟与三模块定向测试命令，共 46 项全部通过，无跳过，包含全部
7 项 Bedrock 测试。模拟记录 19 次请求（17 次成功、2 次预期 429），其中 Bedrock 9 次。
Ruff lint/格式检查通过；未调用真实云服务，未验证 IAM 权限、真实账单或数据库持久化。

### LangChain Core 1.7.3 升级（2026-10-30）

三个仓库同步升级 `langchain-core 1.7.1 → 1.7.3`，仅连带更新 `certifi → 2026.10.23`。
新增的混合内容分片回归在 1.7.1 上复现原始消息被修改的问题，升级后通过；
验证列表内容块后接字符串分片时，原消息、文本输出及 usage 均保持正确。

启动上述 `langchain-compatibility.sim.yaml` 本地模拟后，从集成仓库根目录运行：

```bash
LANGCHAIN_COMPAT_TEST_URL=http://127.0.0.1:49645/provider \
DEEPSEEK_TOOL_IMAGE_TEST_URL=http://127.0.0.1:49645/deepseek/v1 \
  uv run python apps/manage.py test application.tests.test_langchain_compatibility \
  application.tests.test_ai_chat_tool_output models_provider.tests.test_deepseek_tool_images \
  xpack.tests.test_aibot_events --noinput
```

51 项全部通过、无跳过：社区模块 47 项（含全部 7 项 Bedrock），企业微信事件 4 项。
模拟记录 19 次请求（17 次成功、2 次预期 429），其中 Bedrock 9 次。Ruff、三份锁文件和
已安装依赖检查通过。另以新旧 certifi 对 9 个默认公共端点执行匿名 TLS 握手，18 次均通过；
真实模型业务调用、IAM、生产容器、自定义网关及企业代理仍不在验证范围内。
