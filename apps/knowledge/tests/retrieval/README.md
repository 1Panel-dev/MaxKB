# 检索回归测试

常规检索测试：

```bash
python apps/manage.py test knowledge.tests.retrieval
```

## 向量化重启恢复

```bash
python apps/manage.py test knowledge.tests.retrieval.test_embedding_restart
```

worker 启动时，将中断的文档及未完成分段标为失败，刷新分段统计，并释放对应文档的
QueueOnce 锁和执行锁；保留已成功分段。仅重启 Web 服务不重置向量化状态；检测到其他
消费 `celery` 队列的 worker 时跳过恢复。恢复不会自动重新向量化，可在页面选择
“仅执行未成功部分”重试。文档元数据中的恢复标记使重启前延迟重投的消息失效，旧消息
也不能释放新任务的锁。部署时需要同时更新 Web 与 worker 代码。

回归使用独立 PostgreSQL/pgvector 测试库，模拟任务发布和锁后端，不调用实际向量模型。
覆盖文档与分段恢复、历史版本残留、旧消息忽略、Web 单独重启、重复请求状态回滚、
批量跳过活跃任务及提交失败。多节点网络分区和同时启动多个 worker 不在这些测试的验证范围内。

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

## PR #7445 一致性回归（2026-10-26）

审计基准为 v3 `e3afed9b7281c3903855ee13124cc7f0a05052a5`。6 条意见中，
PG 回退的 `meta` 归一化已由 `8c06dd779b1b4e70cdd52ded486e88b300d5c1c3` 修复；
本补丁处理其余 5 条。结论针对代码及合成测试数据，不表示生产环境已发生向量丢失。

| 原始意见 | 基准状态 / 优先级 | 回归覆盖 |
| --- | --- | --- |
| 查询失败导致迁移跳过复制却删除源向量 | 存在，P1 立即修复 | 查询/写入失败、缺失向量、PG 写入失败、外层事务回滚、混合 PG 历史向量 |
| Milvus 残留命中越过 PG 当前知识库/过滤范围 | 存在，P1 立即修复 | 知识库、文档、活动状态、删除/缺失段落复核，以及超过候选上限的残留记录补召回 |
| PG 回退未在 LIMIT 前排除已删除/缺失段落 | 存在，P1 立即修复 | 真实 pgvector 的 embedding / blend 回退 |
| 其他 worker 删除 collection 后缓存不失效 | 存在，P2 修复 | 首次写入失败上抛并清空两个缓存，下次调用重新创建/加载；不隐式吞错重试 |
| 问题向量替换后历史 PG 向量继续参与排名 | 存在，P1 立即修复 | Milvus 写入成功才清空旧 PG 向量，失败保留旧值 |
| PG 回退 meta 为字符串导致下游异常 | 已解决 | 复用 `test_vector_metadata` 与 HTTP fallback 测试 |

运行 PG 一致性测试需要专用 PostgreSQL/pgvector 测试数据库。创建 Django 测试库前，
其模板库应已启用 `vector` 扩展；不要把测试连接指向业务数据库。

```bash
python apps/manage.py test \
  knowledge.tests.retrieval.test_milvus_consistency \
  knowledge.tests.retrieval.test_deleted_paragraphs \
  knowledge.tests.retrieval.test_milvus_write \
  knowledge.tests.retrieval.test_milvus_scope \
  knowledge.tests.retrieval.test_vector_metadata --noinput
```

`test_milvus_consistency.MilvusConsistencyTests` 使用真实 PG，Milvus 操作使用可注入失败的替身；
`test_milvus_write` 使用上文的 Postman 模拟服务运行真实 HTTP 客户端。
另有 `MilvusLiveConsistencyTests`：设置 `MILVUS_LIVE_TEST_URL` 指向**独立、可丢弃的无认证 Milvus**
后运行真实 PG + Milvus 测试。它创建随机 UUID 知识库集合并清理，使用真实事务提交/回滚；
未设置该变量时明确跳过。两个 URL 不可混用，模拟服务 URL 才支持 `/__test/reset`。

迁移先复制全部可迁移向量，再更新锁定的 PG 元数据，源记录只在最外层事务提交后清理。
清理前再次锁定并核对 PG 当前归属，避免延迟回调删除已经迁回源库的向量。
缺失且没有 PG 历史向量兜底的记录使更新失败。清理失败会抛出异常，但此时 PG 已提交且目标向量已存在；
源残留会被 PG 范围复核排除。外层事务回滚则保留源向量，目标可能留下不可见的副本。
这不构成跨存储事务。持久化清理队列、孤儿副本回收、进程崩溃恢复、并发迁移/重建协调，
以及大规模残留数据的补召回性能可以后续优化；本次测试不证明这些场景已得到解决。

本次实际执行：上述 5 个模块共 47 项测试通过，无跳过，其中含 2 项真实 Milvus 2.6.25 集成测试；
其余使用临时 PG17/pgvector、Redis 和 Postman HTTP 模拟服务。新增回归在未修复基准上运行
14 项、出现 19 个失败断言（含子用例）。Ruff check、format --check 和 git diff --check 均通过。
未运行全项目测试、生产数据重放、多节点 Milvus、进程强杀、并发迁移/重建压力测试。
