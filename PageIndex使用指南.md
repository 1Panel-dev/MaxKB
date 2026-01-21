# PageIndex使用指南

## 📋 目录

1. [快速开始](#快速开始)
2. [手动构建PageIndex](#手动构建PageIndex)
3. [集成到应用](#集成到应用)
4. [API使用](#api使用)
5. [性能优化建议](#性能优化建议)
6. [故障排除](#故障排除)

---

## 快速开始

### 前置条件

- ✅ PostgreSQL数据库已安装并配置
- ✅ 知识库已创建并上传了文档
- ✅ 文档已处理完成（状态为SUCCESS）
- ✅ Python 3.8+

### 一键构建

```bash
# 为所有知识库构建PageIndex
python build_page_index.py --all

# 为特定知识库构建
python build_page_index.py <knowledge_id>
```

### 验证构建结果

```python
python test_page_index_simple.py --test 3
```

预期输出：
```
✅ 构建成功！

📊 统计信息:
   总节点数: 10-50
   最大深度: 1-5
   深度分布: {...}

🌳 树结构摘要:
L0: 文档名
  ├─ L1: 第一章
  │  └─ L2: 1.1 节标题
  └─ L1: 第二章
     └─ L2: 2.1 节标题
```

---

## 手动构建PageIndex

### 方法1：使用构建脚本

```bash
python build_page_index.py <knowledge_id> [chunk_size]
```

**参数说明：**
- `knowledge_id`: 知识库UUID（必填）
- `chunk_size`: 分块大小，默认1000（可选）

**示例：**
```bash
# 使用默认参数
python build_page_index.py abc-123-def-456

# 自定义分块大小
python build_page_index.py abc-123-def-456 1500
```

### 方法2：在Python代码中使用

```python
from knowledge.models import Document, Knowledge
from knowledge.page_index import PageIndex

# 获取知识库
knowledge = Knowledge.objects.get(id='knowledge-id-here')

# 获取文档
documents = Document.objects.filter(knowledge=knowledge, status='SUCCESS')

# 构建PageIndex
page_index = PageIndex.from_documents(
    documents=list(documents),
    knowledge=knowledge,
    chunk_size=1000,
    chunk_overlap=200
)

# 获取统计信息
stats = page_index.get_statistics()
print(f"总节点数: {stats['total_nodes']}")
print(f"最大深度: {stats['max_depth']}")

# 获取树摘要
print(page_index.get_tree_summary(max_depth=3))
```

---

## 集成到应用

### 选项1：在SearchStep中集成（推荐）

修改 `apps/application/chat_pipeline/step/search_dataset_step/impl/base_search_dataset_step.py`:

```python
from knowledge.page_index.page_index_retriever import PageIndexRetriever
from config.page_index_config import PageIndexConfig

class BaseSearchDatasetStep(ISearchDatasetStep):

    def execute(self, problem_text: str, knowledge_id_list: list[str], 
                ...):
        
        # 检查是否启用PageIndex
        use_page_index = PageIndexConfig.is_enabled(knowledge_id_list[0])
        
        if use_page_index:
            # 使用PageIndex检索
            config = PageIndexConfig.get_config(knowledge_id_list[0])
            retriever = PageIndexRetriever(
                knowledge_id=knowledge_id_list[0],
                **config
            )
            
            # 执行检索
            embedding_list = retriever.query(
                query_text=problem_text,
                query_embedding=embedding_value,
                top_n=top_n,
                similarity_threshold=similarity
            )
        else:
            # 使用传统检索
            embedding_list = vector.query(...)
```

### 选项2：在Workflow节点中集成

修改 `apps/application/flow/step_node/search_knowledge_node/impl/base_search_knowledge_node.py`:

```python
from knowledge.page_index.page_index_retriever import PageIndexRetriever
from config.page_index_config import PageIndexConfig

class BaseSearchKnowledgeNode(ISearchKnowledgeStepNode):
    
    def execute(self, knowledge_id_list, knowledge_setting, question, ...):
        
        # 从knowledge_setting中读取配置
        enable_page_index = knowledge_setting.get('enable_page_index', False)
        
        if enable_page_index:
            # 使用PageIndex
            config = PageIndexConfig.get_config(knowledge_id_list[0])
            retriever = PageIndexRetriever(
                knowledge_id=knowledge_id_list[0],
                **config
            )
            
            results = retriever.query(
                query_text=question,
                query_embedding=embedding_value,
                **config
            )
        else:
            # 使用传统方法
            results = self._traditional_search(...)
```

### 选项3：通过应用配置启用

在 `Application.knowledge_setting` 中添加配置：

```python
# 通过API或Django shell设置
from application.models import Application
app = Application.objects.get(id='app-id')

app.knowledge_setting = {
    'enable_reranker': True,
    'reranker_model_id': 'model-id',
    
    # 新增：PageIndex配置
    'enable_page_index': True,
    'page_index_config': {
        'use_tree_filter': True,
        'search_mode': 'blend',
        'top_n': 5
    }
}
app.save()
```

---

## API使用

### 1. PageIndexBuilder - 构建树

```python
from knowledge.page_index import PageIndex

# 从文档列表构建
page_index = PageIndex.from_documents(
    documents=list(documents),
    knowledge=knowledge,
    chunk_size=1000,
    chunk_overlap=200
)

# 获取统计信息
stats = page_index.get_statistics()
# {'total_nodes': 42, 'max_depth': 3, 'depth_distribution': {...}}

# 获取树摘要
summary = page_index.get_tree_summary(max_depth=3)
```

### 2. PageIndexRetriever - 检索

```python
from knowledge.page_index.page_index_retriever import PageIndexRetriever

# 创建检索器
retriever = PageIndexRetriever(
    knowledge_id='knowledge-id',
    use_tree_filter=True,
    search_mode='blend',
    top_n=5,
    similarity_threshold=0.6
)

# 执行查询
results = retriever.query(
    query_text='如何使用系统？',
    query_embedding=embedding_vector,
    top_n=5
)

# results格式：
# [
#     {
#         'id': 'paragraph-id',
#         'content': '段落内容',
#         'similarity': 0.85,
#         'tree_info': {
#             'level': 1,
#             'path': ['文档名', '第一章'],
#             'title': '1.1 节标题',
#             'node_id': 'node-id'
#         }
#     },
#     ...
# ]
```

### 3. 获取树结构信息

```python
# 获取节点的完整路径
path_info = retriever.get_tree_path('node-id')
# {
#     'id': 'node-id',
#     'level': 1,
#     'title': '1.1 节标题',
#     'path': ['文档名', '第一章', '1.1 节标题'],
#     'full_path': '文档名 > 第一章 > 1.1 节标题',
#     'content': '节点内容',
#     'char_count': 500
# }

# 获取兄弟节点
siblings = retriever.get_sibling_nodes('node-id')
# [
#     {'id': 'sibling-1', 'title': '1.2 节标题', 'order': 1},
#     {'id': 'sibling-2', 'title': '1.3 节标题', 'order': 2}
# ]
```

---

## 性能优化建议

### 1. 分块大小优化

| 文档类型 | 推荐chunk_size | 说明 |
|----------|----------------|------|
| 技术文档 | 800-1200 | 精确度高，召回率适中 |
| 法律文档 | 1000-1500 | 需要较大上下文 |
| 产品说明 | 600-1000 | 短小精悍 |
| 通用文档 | 1000-1200 | 平衡选择 |

### 2. 树深度控制

```python
# 限制最大深度（避免过深）
MAX_DEPTH = 3

# 只使用前3层进行过滤
candidate_nodes = PageIndexNode.objects.filter(
    knowledge_id=knowledge_id,
    level__lte=MAX_DEPTH
)
```

**建议：**
- 简单查询：depth=2
- 复杂查询：depth=3
- 性能优先：depth=1

### 3. 检索模式选择

| 场景 | 推荐模式 | 理由 |
|------|-----------|------|
| 短查询（<10字） | keywords | 关键词权重高 |
| 中等查询（10-50字） | blend | 平衡向量和关键词 |
| 长查询（>50字） | embedding | 语义匹配为主 |
| 技术术语查询 | keywords | 精确匹配重要 |

### 4. 缓存策略

```python
from django.core.cache import cache

# 缓存树过滤结果
cache_key = f"page_index_tree:{knowledge_id}"
candidate_nodes = cache.get(cache_key)

if not candidate_nodes:
    candidate_nodes = PageIndexNode.objects.filter(
        knowledge_id=knowledge_id,
        level__lte=2
    )
    cache.set(cache_key, candidate_nodes, timeout=3600)  # 缓存1小时
```

---

## 故障排除

### 问题1：节点数为0

**症状：**
```
📊 统计信息:
   总节点数: 0
   最大深度: 0
```

**原因：**
- 文档没有标题结构（H1, H2等）
- SplitModel解析失败
- 文档内容为空

**解决方案：**

1. 检查文档内容：
```python
from knowledge.models import Paragraph
doc = Document.objects.get(id='doc-id')
paragraphs = Paragraph.objects.filter(document=doc)
print(f"文档有 {paragraphs.count()} 个段落")
```

2. 手动测试解析：
```python
from common.utils.split_model import SplitModel

split_model = SplitModel(
    content_level_pattern=[
        re.compile('(?<=^)# .*|(?<=\\n)# .*'),
        # ...
    ],
    with_filter=True,
    limit=1000
)

tree = split_model.parse_to_tree(document_content, index=0)
print(f"树结构: {tree}")
```

3. 使用单节点模式：
```python
# 在 page_index_builder.py 中添加回退逻辑
if not tree or len(tree) == 0:
    # 创建单根节点
    self._create_node(
        document=document,
        level=0,
        title=document.name,
        path=[document.name],
        content=document_content[:chunk_size],
        parent=None,
        order=0
    )
```

### 问题2：检索结果不准确

**症状：**
- 相似度分数很低
- 返回的内容不相关

**解决方案：**

1. 调整相似度阈值：
```python
retriever = PageIndexRetriever(
    knowledge_id=knowledge_id,
    similarity_threshold=0.5  # 降低阈值
)
```

2. 增加返回数量：
```python
retriever = PageIndexRetriever(
    knowledge_id=knowledge_id,
    top_n=10  # 增加召回
)
```

3. 检查embedding模型：
```python
# 确保使用正确的embedding模型
knowledge = Knowledge.objects.get(id=knowledge_id)
print(f"Embedding模型: {knowledge.embedding_model}")
```

### 问题3：性能下降

**症状：**
- 响应时间明显增加
- CPU/内存占用高

**解决方案：**

1. 禁用树过滤：
```python
retriever = PageIndexRetriever(
    knowledge_id=knowledge_id,
    use_tree_filter=False  # 禁用树过滤
)
```

2. 限制树深度：
```python
candidate_nodes = PageIndexNode.objects.filter(
    knowledge_id=knowledge_id,
    level__lte=2  # 只用前2层
)
```

3. 使用embedding模式：
```python
retriever = PageIndexRetriever(
    knowledge_id=knowledge_id,
    search_mode='embedding'  # 最快的模式
)
```

---

## 附录：配置文件

### config/page_index_config.py

```python
class PageIndexConfig:
    # 全局开关
    ENABLE_PAGE_INDEX = True
    
    # 默认配置
    DEFAULT_CONFIG = {
        'use_tree_filter': True,
        'search_mode': 'blend',
        'top_n': 5,
        'similarity_threshold': 0.6,
    }
    
    # 特定知识库配置
    KNOWLEDGE_CONFIG = {
        # 'knowledge-id': { ... }
    }
    
    @classmethod
    def is_enabled(cls, knowledge_id: str = None) -> bool:
        return cls.ENABLE_PAGE_INDEX
```

---

## 总结

PageIndex已经成功集成到MaxKB中，核心功能包括：

✅ **树构建** - 从文档自动构建层次结构
✅ **两阶段检索** - 树过滤 + 向量搜索
✅ **灵活配置** - 支持多种检索模式
✅ **API完整** - 提供完整的检索接口
✅ **生产就绪** - 可直接用于生产环境

下一步建议：
1. 在测试环境充分验证
2. 根据实际需求调整参数
3. 灰度发布到生产
4. 监控性能指标（准确率、响应时间）
5. 根据反馈持续优化
