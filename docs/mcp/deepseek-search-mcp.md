# 在 MaxKB 中接入 DeepSeek 网页搜索 / 网页抓取 MCP 服务

DeepSeek 开放平台提供了两个联网能力接口：

| 接口 | 能力 |
|---|---|
| `POST /v1/tools/search` | 按关键词检索实时网页，返回标题、URL、摘要、发布时间、权威性评分 |
| `POST /v1/tools/fetch` | 抓取指定网页并转换为 Markdown 正文 |

把它们封装成标准 MCP（Model Context Protocol）服务后，MaxKB 的智能体就能在对话中**按需联网**：知识库负责沉淀的领域知识，MCP 工具负责时效性信息，两者互补。

适用场景：

- 知识库问答补时效：先检索知识库，命中不足时自动联网补充最新信息
- 事实核查：对模型生成内容中的事实性断言进行实时核验
- 竞品 / 政策 / 公告跟踪：定期检索指定站点，抓取原文精读

---

## 一、前置条件

| 项目 | 要求 |
|---|---|
| MaxKB | v2（本文按 v2 版本界面撰写） |
| Python | 3.10 及以上（用于运行 MCP 服务） |
| DeepSeek API Key | 开放平台 → API keys 创建，形如 `sk-xxxxxxxx` |

---

## 二、部署 MCP 服务

### 2.1 最小参考实现

仓库中的 [`examples/deepseek_search_mcp_server.py`](../../examples/deepseek_search_mcp_server.py) 是一个可直接运行的完整实现（约 150 行），暴露两个工具：

- `web_search`：网页搜索
- `fetch_page`：网页抓取

```bash
pip install "mcp>=1.9" httpx uvicorn
python examples/deepseek_search_mcp_server.py
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

服务启动后提供两个端点：

| 路径 | 用途 |
|---|---|
| `POST/GET /mcp` | **MCP Streamable HTTP 端点**（MaxKB 填这个） |
| `GET /healthz` | 健康检查 |

### 2.2 自检

```bash
curl http://127.0.0.1:8000/healthz
# {"status":"ok","service":"deepseek-search-mcp"}
```

### 2.3 API Key 的两种给法

| 方式 | 做法 | 适用 |
|---|---|---|
| **MaxKB 侧注入（推荐）** | 在 MaxKB 的 MCP 配置 `headers` 中填 `Authorization: Bearer sk-xxx`，服务按请求透传 | 一套服务供多个应用 / 多个 Key 使用，服务端零配置 |
| 服务端环境变量 | 启动前 `export DEEPSEEK_API_KEY=sk-xxx` | 单一 Key、快速验证 |

参考实现优先读取请求头中的 Key，取不到时回落到环境变量；两者都没有时返回结构化错误提示，不会抛栈中断对话。

### 2.4 生产部署建议

- 用 systemd 或容器托管，`--restart unless-stopped`，非 root 用户运行
- 通过反向代理加 TLS 后再对公网暴露，并用防火墙限制来源 IP
- 日志中不要打印完整 Key（参考实现只在错误信息里保留前 500 字符，且不含请求头）

---

## 三、在 MaxKB 中注册 MCP 服务

进入 **工具 → MCP → 新建**，填写如下配置：

```json
{
  "deepseek-search": {
    "url": "http://<服务所在机器IP>:8000/mcp",
    "transport": "streamable_http",
    "headers": {
      "Authorization": "Bearer sk-xxxxxxxxxxxxxxxx"
    }
  }
}
```

| 字段 | 说明 |
|---|---|
| `deepseek-search` | 服务名，可自定义，后续在应用中按此引用 |
| `url` | MCP 端点，**必须以 `/mcp` 结尾** |
| `transport` | 固定 `streamable_http` |
| `headers.Authorization` | DeepSeek API Key，注意 `Bearer` 与 Key 之间有一个空格 |

保存后 MaxKB 会列出该服务下的工具，正常应显示 `web_search` 与 `fetch_page`。

> **地址填不对是最常见的失败原因**。请站在 MaxKB 所在环境确认可达性：
>
> - MaxKB 与 MCP 服务都在 Docker 中 → 用容器名或 compose 服务名，如 `http://deepseek-search-mcp:8000/mcp`
> - MaxKB 在 Docker、服务在宿主机 → 用宿主机内网 IP
> - **不要填 `127.0.0.1`**：在容器里它指向容器自身，而非宿主机

---

## 四、在应用中使用

### 方式一：智能体应用（模型自动调用）

在应用的「工具」中勾选 `deepseek-search`，并在提示词中说明调用时机，例如：

```
回答涉及实时信息、最新动态或需要事实核查的问题时，先调用 web_search 检索，
再对其中最权威、最相关的 1~2 个 URL 调用 fetch_page 精读原文后作答。
引用来源时标注原始链接。
```

模型会根据问题自行决定是否联网，无需额外编排。

### 方式二：高级编排 / 工作流（显式调用）

在流程中添加「工具」节点，选择 `web_search` 或 `fetch_page`，参数可引用上游变量：

| 工具 | 参数 | 示例 |
|---|---|---|
| `web_search` | `query` | `site:github.com MaxKB MCP` |
| | `count` | `10`（1~50） |
| | `need_content` | `false`（需要正文时置 true，内容较大） |
| `fetch_page` | `url` | 上游 `web_search` 返回的 `results[].url` |
| | `max_chars` | `30000` |

`query` 支持 DeepSeek 的搜索语法：`site:`、`-site:`、`"精确短语"`、`lang:`、`after:`、`before:`。例如 `site:docs.qq.com MaxKB after:2025-01-01`。

---

## 五、验证与排错

| 现象 | 原因与处理 |
|---|---|
| MaxKB 保存时提示连接失败 | 90% 是地址问题：检查是否用了 `127.0.0.1`、防火墙是否放行 8000、容器网络是否互通 |
| 工具列表为空 | 端点路径是否以 `/mcp` 结尾；`transport` 是否为 `streamable_http` |
| 调用返回 401 | API Key 无效或格式错误：确认 `Bearer` 后有空格，Key 未过期、未带引号 |
| 调用返回 429 | 触及 DeepSeek 账号级限速（约 5 QPS）；降低调用频次或错峰 |
| 直接用 `curl` POST `/mcp` 得到 4xx | 正常：MCP 要求先 `initialize` 握手，请用 MaxKB 或 MCP Inspector 测试 |
| 返回 `{"ok": false, ...}` | 参考实现把错误转成结构化 JSON 返回，读 `error.message` 即可定位，不会中断对话 |

建议在终端先确认服务本身正常，再回 MaxKB 侧排查：

```bash
curl http://<服务IP>:8000/healthz
```

---

## 六、计费与限速

- `search` 与 `fetch` **按成功调用次数计费**，请以 DeepSeek 开放平台的最新计价为准
- 账号级限速约 5 QPS；超出返回 429
- 控制成本的实用做法：`web_search` 默认不返回正文（`need_content=false`），只对精选后的少量 URL 调 `fetch_page`；对同一 URL 的重复抓取建议在业务侧做缓存

---

## 七、进阶

参考实现为最小可用版本，生产环境可按需增强：

- 自动重试与指数退避（408 / 429 / 5xx）
- 本地 QPS 限速，避免触碰账号级上限
- 正文截断与字段裁剪，控制 token 消耗
- 更细的错误分类，让模型能根据 `hint` 自动换策略
- 多 Key 隔离与按调用方计量
