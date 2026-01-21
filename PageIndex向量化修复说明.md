# PageIndex向量化修复说明

## 问题描述

**现象**：点击向量化按钮后，`embedding` 表中的 `page_index_node_id` 字段依旧为空（NULL）

**原因**：向量化时序问题
1. 点击"向量化"按钮 → 直接生成 embedding
2. 此时 `page_index_node` 表可能还没有数据
3. `_batch_save()` 中调用 `_resolve_page_index_node_map()` 查询不到节点
4. 导致 `page_index_node_id` 为 NULL

## 根本原因分析

### 原有流程（有问题）

```
用户点击"向量化"
    ↓
embedding_by_document()
    ↓
ListenerManagement.embedding_by_document()
    ↓
_batch_save()
    ↓
_resolve_page_index_node_map()  ← 此时 page_index_node 表可能为空！
    ↓
创建 Embedding 对象（page_index_node_id = NULL）
```

### 问题关键

- **PageIndex 构建时机**：在段落创建后（`_build_page_index_after_paragraph_creation`）
- **向量化时机**：用户手动点击"向量化"按钮
- **时序问题**：如果用户先创建段落，但没有触发 PageIndex 构建，直接点击向量化，则 `page_index_node` 表为空

## 解决方案

### 核心思路

**在向量化之前，先确保 PageIndex 已构建**

### 修改内容

#### 1. 修改 `apps/knowledge/task/embedding.py`

在 `embedding_by_document()` 函数中，**向量化之前**先构建 PageIndex：

```python
@celery_app.task(base=QueueOnce, once={'keys': ['document_id']}, name='celery:embedding_by_document')
def embedding_by_document(document_id, model_id, state_list=None):
    # ... 原有代码 ...
    
    # 【关键修改】在向量化之前先构建PageIndex，确保page_index_node表有数据
    try:
        from knowledge.serializers.common import _build_page_index_for_document_if_needed
        document = QuerySet(Document).filter(id=document_id).first()
        if document:
            _build_page_index_for_document_if_needed(document)
            maxkb_logger.info(f'[PageIndex] Pre-build completed for document {document_id} before embedding')
    except Exception as e:
        maxkb_logger.warning(f'[PageIndex] Pre-build failed for document {document_id}: {e}')
    
    # 生成向量
    embedding_model = get_embedding_model(model_id, exception_handler)
    ListenerManagement.embedding_by_document(document_id, embedding_model, state_list)
    
    # 【保留】向量化后再次同步，确保关联关系正确
    try:
        from knowledge.serializers.common import _sync_page_index_embeddings_for_document
        document = QuerySet(Document).filter(id=document_id).first()
        if document:
            _sync_page_index_embeddings_for_document(document)
    except Exception as e:
        maxkb_logger.warning(f'[PageIndex] Auto sync paragraph embeddings failed: {e}')
```

#### 2. 新增 `apps/knowledge/serializers/common.py` 函数

新增 `_build_page_index_for_document_if_needed()` 函数：

```python
def _build_page_index_for_document_if_needed(document: Document):
    """
    在向量化之前构建PageIndex（如果需要且尚未构建）
    这确保了在生成embedding时，page_index_node表已经有数据
    """
    knowledge = document.knowledge
    
    # 检查PageIndex是否启用
    try:
        from config.page_index_config import PageIndexConfig
        if not PageIndexConfig.is_enabled(str(knowledge.id)):
            return
    except ImportError:
        return
    
    # 检查是否已有段落
    paragraph_count = QuerySet(Paragraph).filter(document=document).count()
    if paragraph_count == 0:
        return
    
    # 检查是否已经构建过PageIndex
    existing_nodes = QuerySet(PageIndexNode).filter(document=document).count()
    if existing_nodes > 0:
        maxkb_logger.info(f'[PageIndex] Already built for document {document.id}, skipping')
        return
    
    # 构建PageIndex
    try:
        maxkb_logger.info(f'[PageIndex] Building for document: {document.name} (ID: {document.id})')
        
        from knowledge.page_index import PageIndex
        
        page_index = PageIndex.from_documents(
            documents=[document],
            knowledge=knowledge,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        stats = page_index.get_statistics()
        maxkb_logger.info(
            f'[PageIndex] Built successfully for document {document.id}: '
            f'{stats["total_nodes"]} nodes, max depth {stats["max_depth"]}'
        )
    except Exception as e:
        maxkb_logger.error(f'[PageIndex] Build error for document {document.id}: {str(e)}', exc_info=True)
```

### 修复后的流程

```
用户点击"向量化"
    ↓
embedding_by_document()
    ↓
_build_page_index_for_document_if_needed()  ← 【新增】先构建PageIndex
    ↓
ListenerManagement.embedding_by_document()
    ↓
_batch_save()
    ↓
_resolve_page_index_node_map()  ← 此时 page_index_node 表已有数据！
    ↓
创建 Embedding 对象（page_index_node_id = 正确的节点ID）
    ↓
_sync_page_index_embeddings_for_document()  ← 【保留】再次同步确保正确
```

## 验证方法

### 1. 运行测试脚本

```bash
python test_page_index_embedding_fix.py
```

### 2. 手动验证

1. 在知识库中上传一个文档
2. 点击"向量化"按钮
3. 查询数据库：

```sql
-- 检查 page_index_node 表
SELECT COUNT(*) FROM page_index_node WHERE document_id = '<your_document_id>';

-- 检查 embedding 表的 page_index_node_id
SELECT 
    COUNT(*) as total,
    COUNT(page_index_node_id) as with_node_id,
    COUNT(*) - COUNT(page_index_node_id) as without_node_id
FROM embedding 
WHERE document_id = '<your_document_id>';
```

**预期结果**：
- `page_index_node` 表有数据
- `embedding` 表的 `page_index_node_id` 字段不为空

## 总结

### 修改文件
1. `apps/knowledge/task/embedding.py` - 修改向量化流程
2. `apps/knowledge/serializers/common.py` - 新增预构建函数

### 核心改进
- **时序保证**：向量化前先构建 PageIndex
- **幂等性**：重复构建会自动跳过
- **容错性**：构建失败不影响向量化流程
- **双重保险**：向量化后再次同步关联关系

### 影响范围
- 仅影响启用了 PageIndex 的知识库
- 对传统检索模式无影响
- 向后兼容，不影响现有数据

