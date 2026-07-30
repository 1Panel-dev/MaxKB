# 检索回归测试

常规检索测试：

```bash
python apps/manage.py test knowledge.tests.retrieval
```

## Milvus 写入 HTTP 回归

使用 Postman CLI 启动仅本机的模拟接口（本次验证版本为 1.74.0）：

```bash
postman simulation run apps/knowledge/tests/fixtures/milvus.sim.yaml --port 49644 --no-history
```

另一个终端运行真实 Python HTTP 客户端的回归测试：

```bash
MILVUS_TEST_URL=http://127.0.0.1:49644/milvus \
  python apps/manage.py test knowledge.tests.retrieval.test_milvus_write
```

未设置 `MILVUS_TEST_URL` 时仍运行建表参数、写入失败上抛的核心单元回归，仅跳过 HTTP 测试。
该地址必须指向本地测试模拟接口：
测试会调用模拟服务专用的 `/__test/reset`、`/__test/state` 控制接口。
测试隔离并恢复 Milvus 配置、Session 与 collection 缓存，使用虚拟凭据和合成向量。
PostgreSQL 查询与模型推理使用测试替身，不连接真实数据库或模型服务。

接口契约来源：

- [Milvus REST v2 创建 collection](https://milvus.io/api-reference/restful/v2.6.x/v2/Collection%20%28v2%29/Create.md)
- [Milvus REST v2 upsert](https://milvus.io/api-reference/restful/v2.6.x/v2/Vector%20%28v2%29/Upsert.md)
- [Milvus 2.6 服务端 JSON 字段定义](https://github.com/milvus-io/milvus/blob/v2.6.0/internal/distributed/proxy/httpserver/request_v2.go)

模拟服务依据上述公开契约编写，未使用提供方的托管 mock。
它检查 `elementTypeParams.dim`、所有 VarChar 字段的 `elementTypeParams.max_length`、主键和实体维度。
测试覆盖创建、加载、写入、加载失败后的重试、删除后重建、批次中途失败、HTTP/业务错误、
无效 JSON、缺失或类型错误的业务码、连接失败，以及段落向量化失败状态和读取时的 PG 兜底。

写入路径要求 HTTP 2xx 且业务 `code` 为整数 `0`；检查、创建、加载或 upsert 失败时抛出
`AppApiException`，阻止后续批次并由调用方更新向量化状态。加载成功与 collection 存在分别缓存，
避免加载失败后的重试被存在性缓存跳过。

这些测试验证客户端与本地 HTTP 契约，不验证真实 Milvus 的索引与检索效果。
异常上抛不提供 PostgreSQL 与 Milvus 的分布式事务：此前成功的批次和已写入的 PG 元数据可能保留；
已有段落重新向量化流程会先清理该段落的旧向量，再重新写入。
