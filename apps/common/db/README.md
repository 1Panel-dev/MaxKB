# v2 → v3 数据库升级

v3 增量迁移按 Django app 合并，统一执行 `python apps/manage.py migrate`。
原先有多个增量文件的 app 仅保留以下升级入口，18 个原 v3 增量文件已删除；
完整保留 v2 的迁移链：

| app | v3 入口 |
| --- | --- |
| application | `0016_v3_upgrade` |
| knowledge | `0012_v3_upgrade` |
| users | `0002_v3_upgrade` |
| system_manage | `0006_v3_upgrade` |

`models_provider/0002_rename_wenxin_provider_to_qianfan`、
`tools/0009_toolworkflowversion_publish_desc` 和 `portal/0001_initial`
本身各只有一个 v3 迁移，直接保留。

合并文件只负责从 v2 升级，按顺序执行普通 Django 迁移操作。
不识别开发期间旧 v3 增量迁移的执行记录，也不支持续跑部分升级的开发数据库。
以下 v2 原始迁移按原文件名、原内容保留在各 app 的 `migrations/` 目录：

- `knowledge.0010_publicfileaccess`：`public_file_access` 表。
- `knowledge.0011_knowledgeworkflow_default_model_setting_and_more`：知识库工作流及版本的默认模型配置。
- `application.0015_application_default_model_setting_and_more`：应用及版本的默认模型配置。

知识库在 v2 的 `0011` 后执行 `0012_v3_upgrade`；
应用在 v2 的 `0015` 后执行 `0016_v3_upgrade`。

已有 v2 数据库由 Django 根据原迁移记录自然跳过已执行的操作；较早 v2 先补齐剩余 v2
迁移，再执行 v3 增量。无需自定义迁移兼容类、手动改写记录或 `--fake`。
v3 不再重复创建 `public_file_access` 和 `default_model_setting`；后者仅同步字段显示名称。
新迁移失败时，当前 app 的变更随事务回滚，可修复原因后重新执行 `migrate`。

升级前备份数据库和文件存储，并先在数据库副本上执行迁移、知识库检索和对话验证。
此迁移处理数据库结构；不将 PG 向量自动搬到 Milvus，也不转换旧工作流的执行逻辑。

## 回归验证

```bash
python apps/manage.py test common.tests.test_v2_migrations
```

迁移回归需要独立的 PostgreSQL 测试实例、创建测试库权限和 `vector` 扩展。
将 `MAXKB_DB_*` 全部指向该测试实例后运行：旧的 `0002_refresh_collation_reindex`
会额外访问配置中的 `DB_NAME` 和 `root` 库，因此不能使用业务库配置执行迁移测试。
回归用例在 Django 创建的测试库中回退并重建迁移状态。
上述三个 v2 原始迁移来自 `origin/v2` 提交 `792a525c5`，应保持原样。
测试直接用 Django 迁移执行器迁移至 v2 的真实依赖节点，写入历史数据后升级至 v3，
验证 v2 基础版本及较新版本升级、公共文件授权、默认模型配置、对话、向量和 Token 数据保留，
以及重复运行不产生额外迁移。
