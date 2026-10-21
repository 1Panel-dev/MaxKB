# 模型提供方测试

运行单元测试：

```bash
uv run python apps/manage.py test models_provider.tests
```

硅基流动图片向量的 HTTP 回归使用 Postman CLI（1.70 或更高版本）运行本地模拟接口。
协议来源为[硅基流动 Embeddings API](https://api-docs.siliconflow.cn/docs/api/embeddings-post)。
模拟返回固定测试向量，用于检查请求格式、图片顺序和响应解析。

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
测试用合成细长图片复现超过 200:1 的拒绝响应，验证请求前补白边后，真实 DashScope SDK 的批量请求成功且顺序不变。
补白边仅用于 Qwen3 的内嵌图片请求，原始文件、正常尺寸图片和远程 URL 保持不变；远程 URL 的图片仍由上游检查。
内嵌 SVG（包括徽章中的嵌套 SVG 图标）使用 [resvg-py](https://github.com/baseplate-admin/resvg-py)
在请求前按原尺寸转为白底 PNG；只有最长边超过 2048 像素时才等比缩小，再执行细长图片补边。
尺寸在栅格化前计算，避免先生成巨幅位图。支持 `width`/`height`、`viewBox`、百分比和常见物理单位
（按 96 DPI 换算）；两者均未指定时使用 300×150 视口。88×20 的 SVG 只补白边至 88×32，不放大内容。
此步骤仅转换请求副本，保留原始 SVG 文件；外部图片资源会被拒绝，超链接不参与渲染。
依赖由根项目和 community 的 `pyproject.toml` 声明，更新环境时执行 `uv sync`，并重启向量化 worker。
HTTP 回归覆盖 SVG/PNG 混合批量请求，单元测试检查嵌套图标、像素、尺寸和外部资源限制。
模拟返回固定向量，不验证百炼实际模型的推理结果。未设置上述环境变量时跳过 HTTP 回归。
