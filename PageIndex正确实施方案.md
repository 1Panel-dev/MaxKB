# PageIndex正确实施方案 - MaxKB无缝集成

> **版本**: v2.0
> **日期**: 2026-01-20
> **目标**: 按照"PageIndex技术分析与实施方案"正确集成PageIndex到MaxKB，实现用户无感知

---

## 问题复盘

### 当前方案的问题

**错误的触发时机：**
```python
# listener_manage.py:295
def embedding_by_document(document_id, embedding_model: Embeddings, state_list=None):
    # ... 向量化段落 ...
    # 检查是否存在索引
    create_knowledge_index(document_id=document_id)  # ❌ 错误：在向量化完成后才触发
```

**错误依赖关系：**
```python
# common.py:305-309 (我的错误修改)
# 知识库模式：构建所有已成功处理的文档
documents = list(QuerySet(Document).filter(
    knowledge=knowledge,
    status='SUCCESS'  # ❌ 错误：依赖文档SUCCESS状态
))
```

### 问题根源

1. **PageIndex构建时机错误**：放在了embedding完成后
2. **依赖向量化状态**：等待SUCCESS才构建
3. **违背PageIndex设计理念**：PageIndex应该独立于向量化，只依赖段落内容

---

## 正确方案：基于技术方案

### 核心原则（来自PageIndex技术方案）

根据技术方案第3.3节和第7.3节：

> "PageIndex应该在文档解析完成后立即构建，不依赖向量化状态"
> "PageIndex节点的向量化应该异步进行，不阻塞主流程"

### 实施架构

```
文档上传流程：
├── 1. 文件解析
│   └── 生成段落列表（Paragraph表）
├── 2. 批量创建段落 ✅ (knowledge.py:563)
│   └── QuerySet(Paragraph).bulk_create(paragraph_model_list)
├── 3. 触发PageIndex构建 ✅ 【新增】
│   └── _build_page_index_after_paragraph_creation(document_id)
├── 4. 触发段落向量化 ✅ (listener_manage.py:254)
│   └── ListenerManagement.embedding_by_document(document_id, embedding_model)
└── 5. PageIndex节点异步向量化 ✅ 【新增】
    └── Celery任务：generate_page_index_embeddings.delay(document_id)
```

**关键改进：**
- ✅ **步骤3和步骤4并行**：PageIndex构建与向量化异步并行
- ✅ **不依赖SUCCESS状态**：只要段落创建完成就构建
- ✅ **用户无感知**：PageIndex自动构建，无需手动触发

---

## 实施步骤

### 步骤1：在段落创建后触发PageIndex构建

**文件：** `apps/knowledge/serializers/knowledge.py`

**位置：** 第563行 `QuerySet(Paragraph).bulk_create(paragraph_model_list)` 之后

**修改：**

```python
# 第563行之后添加：
# 批量插入段落
QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None

# 【新增】段落创建完成后触发PageIndex构建（用户无感知）
if len(document_model_list) > 0:
    try:
        from knowledge.serializers.common import _build_page_index_for_documents
        document_ids = [str(doc.id) for doc in document_model_list]
        _build_page_index_for_documents(document_ids)
    except Exception as e:
        # PageIndex构建失败不影响主流程
        from common.utils.logger import maxkb_logger
        maxkb_logger.warning(f'Auto build PageIndex failed: {str(e)}')
```

---

### 步骤2：实现PageIndex构建函数

**文件：** `apps/knowledge/serializers/common.py`

**新增函数：**

```python
def _build_page_index_for_documents(document_ids: List[str]):
    """
    在段落创建后自动构建PageIndex（不依赖向量化状态）

    Args:
        document_ids: 文档ID列表
    """
    from knowledge.models import Document, PageIndexNode
    from knowledge.page_index import PageIndex
    from django.db.models import QuerySet

    for doc_id in document_ids:
        document = QuerySet(Document).filter(id=doc_id).first()
        if not document:
            continue

        knowledge = document.knowledge

        # 检查PageIndex是否启用
        try:
            from config.page_index_config import PageIndexConfig
            if not PageIndexConfig.is_enabled(str(knowledge.id)):
                continue
        except ImportError:
            continue

        # 检查是否已有段落
        from knowledge.models import Paragraph
        paragraph_count = QuerySet(Paragraph).filter(document=document).count()
        if paragraph_count == 0:
            continue

        # 构建PageIndex（不等待向量化）
        try:
            maxkb_logger.info(f'[PageIndex] Auto building for document: {document.name} (ID: {doc_id})')

            # 清理旧PageIndex数据
            QuerySet(PageIndexNode).filter(document=document).delete()

            # 构建新PageIndex树
            page_index = PageIndex.from_documents(
                documents=[document],
                knowledge=knowledge,
                chunk_size=1000,
                chunk_overlap=200
            )

            stats = page_index.get_statistics()
            maxkb_logger.info(
                f'[PageIndex] Built successfully for document {doc_id}: '
                f'{stats["total_nodes"]} nodes, max depth {stats["max_depth"]}'
            )

        except Exception as e:
            maxkb_logger.error(f'[PageIndex] Build error for document {doc_id}: {str(e)}', exc_info=True)
```

---

### 步骤3：实现PageIndex节点异步向量化

**文件：** 新建 `apps/knowledge/tasks.py`

**内容：**

```python
from celery import shared_task
from knowledge.models import PageIndexNode
from models_provider.tools import get_model
from langchain_core.embeddings import Embeddings
from django.db.models import QuerySet


@shared_task
def generate_page_index_embeddings(document_id: str):
    """
    异步生成PageIndex节点的嵌入向量

    Args:
        document_id: 文档ID
    """
    from knowledge.models import Document, Knowledge
    from knowledge.page_index import PageIndex
    from common.utils.logger import maxkb_logger

    document = QuerySet(Document).filter(id=document_id).first()
    if not document:
        maxkb_logger.warning(f'[PageIndex] Document not found: {document_id}')
        return

    knowledge = document.knowledge

    # 获取向量化模型
    embedding_model = knowledge.embedding_model
    if not embedding_model:
        maxkb_logger.warning(f'[PageIndex] No embedding model for knowledge: {knowledge.id}')
        return

    # 获取embedding客户端
    try:
        embedding_client = get_model(
            str(embedding_model.id),
            embedding_model.model_credential
        )
    except Exception as e:
        maxkb_logger.error(f'[PageIndex] Failed to get embedding model: {e}')
        return

    # 获取所有待向量化的PageIndex节点
    nodes = QuerySet(PageIndexNode).filter(document=document)

    maxkb_logger.info(f'[PageIndex] Starting embedding generation for {nodes.count()} nodes')

    # 批量生成嵌入
    for node in nodes:
        try:
            if len(node.content) == 0:
                continue

            # 生成嵌入向量
            embedding = embedding_client.embed_query(node.content)

            # 更新节点的embedding字段
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE page_index_node SET embedding = %s::vector WHERE id = %s",
                    (str(embedding), str(node.id))
                )

        except Exception as e:
            maxkb_logger.error(f'[PageIndex] Failed to embed node {node.id}: {e}')

    maxkb_logger.info(f'[PageIndex] Embedding generation completed for document {document_id}')
```

---

### 步骤4：在PageIndexBuilder中调度异步向量化

**文件：** `apps/knowledge/page_index/page_index_builder.py`

**修改 `_process_single_document` 方法，在最后添加调度：**

```python
def _process_single_document(
    self,
    document: Document,
    chunk_size: int,
    chunk_overlap: int
):
    """处理单个文档"""
    print(f"[PageIndex] Processing document: {document.name} (ID: {document.id})")

    # ... 现有的树构建代码 ...

    print(f"[PageIndex] Document processing completed: {document.name}")

    # 【新增】调度异步向量化任务
    try:
        from knowledge.tasks import generate_page_index_embeddings
        generate_page_index_embeddings.delay(str(document.id))
        print(f"[PageIndex] Async embedding task scheduled for document: {document.id}")
    except ImportError:
        print("[PageIndex] Warning: Celery not available, embedding not scheduled")
    except Exception as e:
        print(f"[PageIndex] Error scheduling embedding: {e}")
```

---

### 步骤5：删除错误的自动构建逻辑

**文件：** `apps/knowledge/serializers/common.py`

**删除 `_auto_build_page_index` 函数中错误的逻辑：**

```python
# 删除这个函数中的代码：
# ❌ 错误：依赖文档SUCCESS状态
# documents = list(QuerySet(Document).filter(
#     knowledge=knowledge,
#     status='SUCCESS'  # 删除这个依赖
# ))
```

**或者完全删除 `_auto_build_page_index` 函数**，因为PageIndex已经在段落创建后构建了。

**保留 `create_knowledge_index` 中的向量索引创建逻辑，但删除PageIndex构建：**

```python
def create_knowledge_index(knowledge_id=None, document_id=None):
    # ... 现有的向量索引创建逻辑 ...
    # 删除：_auto_build_page_index(knowledge_id=k_id, document_id=document_id)
```

---

### 步骤6：配置PageIndex开关

**文件：** `config/page_index_config.py`（已存在）

**确保配置正确：**

```python
class PageIndexConfig:
    # 全局开关
    ENABLE_PAGE_INDEX = True

    # 默认配置
    DEFAULT_CONFIG = {
        'use_tree_filter': True,        # 使用树过滤
        'search_mode': 'blend',            # 检索模式
        'top_n': 5,                      # 返回数量
        'similarity_threshold': 0.6,        # 相似度阈值
    }

    @classmethod
    def is_enabled(cls, knowledge_id: str = None) -> bool:
        """检查PageIndex是否启用"""
        if not cls.ENABLE_PAGE_INDEX:
            return False
        return True
```

---

## 检索部分修改（技术方案第3.4节）

### 当前检索流程

```python
# pg_vector.py
class VectorSearch(ISearch):
    def handle(self, query_set, query_text, query_embedding, top_number, similarity, search_mode):
        # 传统向量搜索，没有树导航
        exec_sql = get_file_content('embedding_search.sql')
        return embedding_model
```

### 需要修改的内容

**技术方案第3.4节指出需要实现两阶段检索：**

1. **阶段1：树导航**（粗选）
2. **阶段2：向量搜索**（精选）
3. **阶段3：Reranker精排**（可选）

**实施方式：**

#### 方案A：在现有VectorSearch中集成PageIndex（推荐）

修改 `apps/knowledge/vector/pg_vector.py`：

```python
class VectorSearch(ISearch):
    def handle(self, query_set, query_text, query_embedding, top_number, similarity, search_mode):
        # 检查是否启用PageIndex
        knowledge_id = self._get_knowledge_id_from_queryset(query_set)

        try:
            from config.page_index_config import PageIndexConfig
            if PageIndexConfig.is_enabled(knowledge_id):
                # 使用PageIndex检索
                from knowledge.page_index import PageIndexRetriever
                retriever = PageIndexRetriever(knowledge_id=knowledge_id)

                # 执行两阶段检索
                results = retriever.query(
                    query_text=query_text,
                    query_embedding=query_embedding,
                    top_n=top_number,
                    similarity_threshold=similarity
                )
                return results
        except ImportError:
            pass  # PageIndex不可用时回退到传统搜索

        # 回退到传统向量搜索
        exec_sql = get_file_content('embedding_search.sql')
        return embedding_model
```

#### 方案B：作为独立的检索模式（备选）

在知识库设置中添加"检索模式"选项：
- 传统模式（向量搜索）
- PageIndex模式（树导航 + 向量搜索）

用户可以选择使用哪种检索模式。

---

## 完整流程验证

### 用户导入文档后的流程

```
用户操作：上传Excel文件
    ↓
1. 文件解析 → 生成段落列表
    ↓
2. 批量创建段落（Paragraph表）✅
    ↓
3. 自动触发PageIndex构建 ✅ 【用户无感知】
    ├── 解析树结构（SplitModel）
    ├── 创建PageIndexNode记录
    └── 调度异步向量化任务
    ↓
4. 并行：段落向量化（Embedding表）✅
    ↓
5. PageIndex节点异步向量化 ✅
    ↓
完成：
- 段落已向量化（传统检索可用）
- PageIndex已构建（树结构可用）
- PageIndex节点已向量化（新检索模式可用）
```

### 用户查询时的流程

```
用户提问："如何配置Reranker？"
    ↓
检查知识库是否启用PageIndex
    ↓
【启用PageIndex】：
    阶段1：树导航
        LLM分析查询 → 确定目标章节 → ["第一章", "RAG优化", "配置方法"]
    ↓
    阶段2：向量搜索
        在候选章节内检索 → Top-N结果
    ↓
    阶段3：Reranker精排
        Cross-Encoder重排序 → 最终结果
    ↓
【未启用PageIndex】：
    直接向量搜索 → 传统结果
```

---

## 实施时间表

### 阶段1：PageIndex构建集成（1天）
- [x] 数据模型已存在（PageIndexNode表）
- [ ] 在段落创建后触发PageIndex构建
- [ ] 实现PageIndex异步向量化任务
- [ ] 删除错误的自动构建逻辑

### 阶段2：检索集成（1-2天）
- [ ] 实现PageIndexRetriever两阶段检索
- [ ] 在VectorSearch中集成PageIndex
- [ ] 添加配置开关

### 阶段3：测试验证（1天）
- [ ] 单元测试：PageIndex构建
- [ ] 集成测试：完整导入-检索流程
- [ ] 性能测试：响应时间、准确率

### 阶段4：灰度发布（持续）
- [ ] 配置开关，默认关闭
- [ ] 选择测试知识库启用
- [ ] 监控准确率和性能
- [ ] 根据反馈优化

---

## 总结

### 核心改进

1. ✅ **正确的触发时机**：段落创建后立即触发，不依赖向量化
2. ✅ **用户无感知**：PageIndex自动构建，无需手动操作
3. ✅ **异步处理**：PageIndex节点向量化不阻塞主流程
4. ✅ **向后兼容**：未启用PageIndex时使用传统检索
5. ✅ **可配置**：通过配置文件控制开启/关闭

### 关键文件修改

1. `apps/knowledge/serializers/knowledge.py` - 段落创建后触发
2. `apps/knowledge/serializers/common.py` - 实现PageIndex构建
3. `apps/knowledge/tasks.py` - 新建：异步向量化任务
4. `apps/knowledge/page_index/page_index_builder.py` - 调度异步任务
5. `apps/knowledge/vector/pg_vector.py` - 集成PageIndex检索

### 下一步

请确认此方案后，我将按照步骤逐一实施修改。
