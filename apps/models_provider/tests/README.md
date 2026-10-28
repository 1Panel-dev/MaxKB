# 模型提供方测试

运行单元测试：

```bash
uv run python apps/manage.py test models_provider.tests
```

硅基流动图片向量的 HTTP 回归使用 Postman CLI（1.70 或更高版本）运行本地模拟接口。
协议来源为[硅基流动 Embeddings API](https://api-docs.siliconflow.cn/docs/api/embeddings-post)。
模拟返回测试向量（图片使用实际收到的 PNG 宽高），用于检查请求格式、图片顺序和响应解析。

在一个终端启动模拟接口：

```bash
postman simulation run apps/models_provider/tests/fixtures/siliconflow.sim.yaml --port 49641 --no-history
```

在另一个终端运行 HTTP 回归：

```bash
SILICONFLOW_EMBEDDING_TEST_URL=http://127.0.0.1:49641/siliconflow/v1 \
  uv run python apps/manage.py test models_provider.tests.test_embedding_capabilities
```

测试使用虚拟 API Key 和图片数据；未设置该环境变量时跳过 HTTP 回归。
这些检查验证本地接口协议，真实模型的向量效果需要在实际环境验证。

百炼 Qwen3 图片向量的 HTTP 回归同样使用本地模拟接口：

```bash
postman simulation run apps/models_provider/tests/fixtures/aliyun.sim.yaml --port 49642 --no-history
```

在另一个终端运行：

```bash
ALIYUN_EMBEDDING_TEST_URL=http://127.0.0.1:49642/aliyun/api/v1 \
  uv run python apps/manage.py test models_provider.tests.test_aliyun_embedding_images
```

协议依据为[百炼多模态向量 API](https://help.aliyun.com/zh/model-studio/multimodal-embedding-api-reference)，
图片长宽比限制依据为[Qwen3-VL 图片预处理器](https://github.com/QwenLM/Qwen3-VL/blob/main/qwen-vl-utils/src/qwen_vl_utils/vision_process.py)。
测试用合成细长图片复现超过 200:1 的拒绝响应，验证请求前补白边后，真实 DashScope SDK 的逐张请求成功且顺序不变。
百炼 Qwen3 对内嵌图片补白边，原始文件、正常尺寸图片和远程 URL 保持不变；远程 URL 的图片仍由上游检查。
内嵌 SVG（包括徽章中的嵌套 SVG 图标）使用 [resvg-py](https://github.com/baseplate-admin/resvg-py)
在请求前按原尺寸转为白底 PNG；只有最长边超过 2048 像素时才等比缩小，再执行细长图片补边。
尺寸在栅格化前计算，避免先生成巨幅位图。支持 `width`/`height`、`viewBox`、百分比和常见物理单位
（按 96 DPI 换算）；两者均未指定时使用 300×150 视口。88×20 的 SVG 只补白边至 88×32，不放大内容。
此步骤仅转换请求副本，保留原始 SVG 文件；外部图片资源会被拒绝，超链接不参与渲染。
依赖由根项目和 community 的 `pyproject.toml` 声明，更新环境时执行 `uv sync`，并重启向量化 worker。
HTTP 回归覆盖 SVG/PNG 混合输入，单元测试检查嵌套图标、像素、尺寸和外部资源限制。
百炼多模态图片向量统一逐张顺序调用，每次仅发送一张图片；例如 15 张图片发送 15 次请求。
每次必须返回一个向量，再按输入顺序合并。回归覆盖空输入、多种模型、返回数量异常及后续图片失败。
HTTP 回归通过真实 DashScope SDK 验证 11、15、20、21 张图片均逐张发送，并保持结果数量、顺序和维度。
模拟返回固定向量，不验证百炼实际模型的推理结果。未设置上述环境变量时跳过 HTTP 回归。

## 公共图片处理与跨提供商回归

`models_provider.embedding_image.prepare_embedding_image` 统一处理内嵌 SVG，百炼、硅基流动、
腾讯 TokenHub 和火山引擎的图片向量化均复用此函数。SVG 按原视口渲染，最长边默认最多 2048，
仅大图等比缩小；再按模型要求扩展白色画布，不放大或裁剪图片内容。
最小边长、最大长宽比、最小像素总量、SVG 渲染边长和像素总量上限通过独立参数传入。

| 模型 | 补边与渲染限制 | 88×20 SVG 的请求尺寸 |
| --- | --- | --- |
| 百炼 / 硅基流动 Qwen3-VL-Embedding | 最小边长 32，最大长宽比 200:1 | 88×32 |
| 腾讯 TokenHub Kinfra-VL-Embedding | 最小像素总量 4096；SVG 渲染最多 1843200 像素 | 88×47 |
| 百炼其他多模态模型 / 火山 Doubao-Embedding-Vision | 通用 SVG 渲染，未配置额外补边 | 88×20 |

腾讯的像素总量限制依据为 [TokenHub Embedding 文档](https://intl.cloud.tencent.com/document/product/1300/81297)。
这是面积限制，不能直接当作两个边长都至少为 64。腾讯在公共处理之后再移除 data URL 前缀，
其他提供商继续使用 PNG data URL。正常栅格图片不统一缩小，仅按已配置的最小尺寸规则补边。
远程 URL 与无法识别为 data URL 的提供商输入原样透传，不增加服务端下载行为；
本地 SVG 文件经知识库转换为 data URL 后才进入公共处理。未增加新的生产依赖。

一次启动全部相关模拟接口：

```bash
postman simulation run apps/models_provider/tests/fixtures/multimodal.sim.yaml --port 49643 --no-history
```

另一个终端运行完整回归：

```bash
MULTIMODAL_EMBEDDING_TEST_URL=http://127.0.0.1:49643 \
ALIYUN_EMBEDDING_TEST_URL=http://127.0.0.1:49643/aliyun/api/v1 \
SILICONFLOW_EMBEDDING_TEST_URL=http://127.0.0.1:49643/siliconflow/v1 \
  uv run python apps/manage.py test models_provider.tests.test_embedding_images \
  models_provider.tests.test_aliyun_embedding_images models_provider.tests.test_embedding_capabilities
```

聚合模拟复用仓库已有的百炼、硅基流动协议，并依据腾讯文档和
[火山多模态向量 API](https://docs.volcengine.com/docs/ark/multimodal-vectorization-api?lang=zh)
补充腾讯、火山协议。HTTP 回归运行真实 DashScope / Ark SDK 和 requests 客户端，
验证 SVG/PNG 顺序、最终图片尺寸、Base64 格式、文本请求及外部 SVG 资源拒绝。
所有请求使用合成图片和虚拟密钥，仅验证本地预处理和接口协议，不调用真实模型或验证检索质量。

## DeepSeek 适配器的工具图片

工具返回的图片在请求中转入紧随该批工具响应的 user 消息，保留图片顺序、调用 ID 和
assistant 的 `reasoning_content`；原始 ToolMessage、执行记录和用户已有图片不改写。
此路径用于通过 DeepSeek 适配器接入支持视觉的兼容网关，不代表所有 DeepSeek 模型支持图片。

```bash
postman simulation run apps/models_provider/tests/fixtures/deepseek-tool-images.sim.yaml --port 49644 --no-history --output ndjson
```

另一个终端运行：

```bash
DEEPSEEK_TOOL_IMAGE_TEST_URL=http://127.0.0.1:49644/deepseek/v1 \
  uv run python apps/manage.py test models_provider.tests.test_deepseek_tool_images \
  application.tests.test_ai_chat_tool_output
```

模拟契约来自 v2 的工具图片适配和当前 OpenAI SDK 消息格式，返回收到的消息结构，
用于验证同步调用、异步流式请求及并行工具响应顺序，不验证真实模型的视觉推理结果。
未设置该环境变量时只跳过两项 HTTP 测试，其余请求构造和消息流测试照常运行。
