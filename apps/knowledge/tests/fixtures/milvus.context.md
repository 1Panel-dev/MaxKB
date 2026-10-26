# Milvus regression simulation

2026-10-26：复用仓库的 REST v2 契约模拟器，补充按 ID 查询和删除；实现见 `milvus/default.js`。

## Purpose

唯一成员 `milvus` 用于真实 Python HTTP 客户端的错误传播、查询完整性和集合缓存回归。
PG 事务、范围过滤由 `../retrieval/test_milvus_consistency.py` 验证。

## Execution

从 community 仓库根目录运行：

```bash
postman simulation run apps/knowledge/tests/fixtures/milvus.sim.yaml --port 49645 --no-history --output ndjson
MILVUS_TEST_URL=http://127.0.0.1:49645/milvus python apps/manage.py test knowledge.tests.retrieval.test_milvus_write
```

运行输出中的 request 事件和测试的 `/__test/state` 断言用于确认请求到达模拟服务；结束后停止 CLI。

## Assumptions

- 模拟器不实现 ANN 检索或分布式一致性；需要真实 Milvus 的测试使用独立的 `MILVUS_LIVE_TEST_URL`。
  2026-10-26 已在本机 Milvus 2.6.25 单机实例验证复制/清理、事务回滚及缓存恢复，不能推导集群故障保证。
- 此次使用临时 PG17 + pgvector 和 Redis；新建 Django 测试库前须在模板库启用 vector。
  测试连接及日志目录通过临时 settings 覆盖，未修改仓库运行配置。（2026-10-26 实测）

## Observations

<!-- begin:observations -->
2026-10-26：唯一成员 milvus 收到 has/create/load/upsert/query/delete/drop 请求；没有未触达的成员。
新增故障用例在原始 v3 上失败，修复后的 HTTP 回归通过。
<!-- end:observations -->

## What didn't work

- 2026-10-26：受限沙箱的本机监听/连接返回 `Operation not permitted`，需允许本机网络；
  默认日志目录 `/opt/maxkb/logs` 不可写，使用临时 settings 将日志指向可写临时目录。
