# PageIndex测试步骤说明

## 📋 快速测试指南

### 步骤1: 验证数据库迁移（已完成）
```bash
python manage.py migrate knowledge
```
✅ **确认**: 看到 "Running migrations: OK" 表示迁移成功

---

### 步骤2: 运行自动化测试

#### 选项A: 运行所有测试
```bash
python test_page_index_simple.py
```

#### 选项B: 分步测试

**测试1 - 数据库检查**
```bash
python test_page_index_simple.py --test 1
```
- 验证 `PageIndexNode` 表是否创建成功
- 验证 `Embedding` 表是否添加了PageIndex字段

**测试2 - 列出知识库**
```bash
python test_page_index_simple.py --test 2
```
- 显示所有可用的知识库
- 显示每个知识库的文档数量

**测试3 - 构建PageIndex（核心测试）**
```bash
python test_page_index_simple.py --test 3
```
- 从文档构建PageIndex树结构
- 显示统计信息（节点数、深度、分布）
- 显示树结构摘要

**测试4 - 检索功能**
```bash
python test_page_index_simple.py --test 4
```
- 验证PageIndexRetriever是否可以创建
- 显示检索器配置

---

### 步骤3: 手动构建PageIndex（可选）

如果你想为特定知识库构建PageIndex：

```bash
python build_page_index.py <knowledge_id>
```

示例：
```bash
# 先列出所有知识库
python manage.py shell
>>> from knowledge.models import Knowledge
>>> Knowledge.objects.all().values('id', 'name')

# 退出shell
>>> exit()

# 为特定知识库构建
python build_page_index.py <替换为实际的知识库ID>
```

为所有知识库构建：
```bash
python build_page_index.py --all
```

---

## 🧪 测试结果解读

### ✅ 成功的输出示例

```
============================================================
测试1: 检查数据库表
============================================================
✅ PageIndexNode表存在，当前有 0 个节点
✅ Embedding表有PageIndex关联: True

============================================================
测试2: 列出可用知识库
============================================================
找到 1 个知识库:

1. 我的知识库
   ID: 123e4567-e89b-12d3-a456-426614174000
   文档数: 5

============================================================
测试3: 构建PageIndex
============================================================
使用知识库: 123e4567-e89b-12d3-a456-426614174000
找到 5 个文档，开始构建...

✅ 构建成功！

📊 统计信息:
   总节点数: 42
   最大深度: 3
   深度分布: {0: 1, 1: 5, 2: 18, 3: 18}

🌳 树结构摘要:
L0: Root (1个节点)
├─ L1: 第一章：概述 (5个节点)
│  ├─ L2: 1.1 背景 (3个节点)
│  └─ L2: 1.2 目标 (3个节点)
...
```

---

## ⚠️ 常见问题与解决方案

### 问题1: 迁移失败
**错误**: `ProgrammingError: relation "page_index_node" already exists`

**解决**:
```bash
# 回滚迁移
python manage.py migrate knowledge 0007 --fake

# 删除表
python manage.py dbshell
> DROP TABLE IF EXISTS page_index_node;

# 退出
> \q

# 重新运行迁移
python manage.py migrate knowledge
```

### 问题2: 没有知识库
**错误**: `❌ 没有找到任何知识库`

**解决**:
- 你需要先创建知识库并上传文档
- 可以通过MaxKB的Web界面创建

### 问题3: 测试3失败
**错误**: `❌ 构建失败: No module named 'knowledge.page_index'`

**解决**:
- 检查 `apps/knowledge/page_index/` 目录是否存在
- 检查 `__init__.py` 文件是否正确

### 问题4: 文档解析失败
**错误**: `❌ 构建失败: 无法解析文档结构`

**解决**:
- 某些文档可能没有结构化的标题（H1, H2等）
- PageIndex会自动降级为单节点结构
- 这是正常的，不影响功能

---

## 📊 测试清单

运行以下命令检查所有功能：

```bash
# 1. 验证数据库迁移
python manage.py migrate knowledge

# 2. 运行完整测试
python test_page_index_simple.py

# 3. 如果测试3成功，检查数据库
python manage.py shell
>>> from knowledge.models import PageIndexNode
>>> PageIndexNode.objects.count()
# 应该返回大于0的数字

# 4. 查看树结构
>>> from knowledge.models import PageIndexNode
>>> nodes = PageIndexNode.objects.filter(level=0)
>>> for node in nodes:
...     print(f"根节点: {node.title}")
...     for child in node.children.all():
...         print(f"  └─ {child.title}")
```

---

## 🎯 下一步

### 如果所有测试通过 ✅

1. **继续阶段4-5**（集成到检索流程）
2. **开始性能测试**（对比传统分块 vs PageIndex）
3. **准备灰度发布**

### 如果部分测试失败 ❌

1. **检查错误信息**
2. **查看上面的常见问题解决方案**
3. **提供错误日志，我帮你解决**

---

## 📝 测试报告模板

完成测试后，请填写以下报告：

```
=== PageIndex测试报告 ===

测试日期: __________
测试人员: __________

测试结果:
[ ] 数据库迁移成功
[ ] 测试1通过 - 数据库检查
[ ] 测试2通过 - 列出知识库
[ ] 测试3通过 - 构建PageIndex
[ ] 测试4通过 - 检索功能

统计信息:
- 知识库数量: ___
- 总文档数: ___
- PageIndex节点数: ___
- 最大深度: ___

遇到的问题:
___________________________
___________________________

建议:
___________________________
___________________________
```
