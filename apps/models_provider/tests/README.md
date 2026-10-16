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
