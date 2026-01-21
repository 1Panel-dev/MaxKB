# MaxKB检索测试方法说明

## 🎯 核心结论

**MaxKB的检索测试 ≠ 必须依赖问题生成！**

MaxKB提供了两种独立的测试方式：
1. ✅ **命中测试（Hit Test）** - 直接测试检索，无需问题生成
2. ⚠️ **问题生成（Problem Generation）** - 可选功能，用于自动生成测试问题

---

## 📋 方式一：命中测试（Hit Test）- 推荐

### 1.1 功能说明

**命中测试**是MaxKB内置的检索质量测试工具，可以：
- ✅ 直接输入查询文本
- ✅ 实时查看检索结果
- ✅ 调整检索参数（Top-N、相似度、检索模式）
- ✅ 查看每个段落的相似度分数
- ✅ **完全独立，不依赖问题生成**

### 1.2 使用方法

#### **通过UI界面**

1. 进入知识库详情页
2. 点击"命中测试"标签
3. 输入测试问题
4. 调整参数：
   - **检索模式**: embedding（向量）/ keywords（关键词）/ blend（混合）
   - **Top-N**: 返回结果数量（默认5）
   - **相似度阈值**: 最低相似度（默认0.6）
5. 点击发送，查看检索结果

**代码位置**:
- 前端: `ui/src/views/hit-test/index.vue`
- 后端API: `apps/knowledge/views/knowledge.py` (HitTest类)
- 核心逻辑: `apps/knowledge/vector/pg_vector.py` (hit_test方法)

#### **通过API调用**

```bash
curl -X PUT "http://localhost:8080/api/knowledge/{knowledge_id}/hit_test" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "如何优化RAG系统的召回率？",
    "top_number": 5,
    "similarity": 0.7,
    "search_mode": "blend"
  }'
```

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "paragraph_id": "xxx-xxx-xxx",
      "title": "RAG优化方案",
      "content": "召回率提升可以通过...",
      "similarity": 0.85,
      "comprehensive_score": 0.85,
      "document_name": "RAG技术文档.pdf"
    },
    ...
  ]
}
```

### 1.3 核心代码

<augment_code_snippet path="apps/knowledge/vector/pg_vector.py" mode="EXCERPT">
```python
def hit_test(self, query_text, knowledge_id_list: list[str], 
             exclude_document_id_list: list[str], top_number: int,
             similarity: float, search_mode: SearchMode, embedding: Embeddings):
    # 直接使用query_text进行检索，无需预先生成问题
    embedding_query = embedding.embed_query(query_text)
    query_set = QuerySet(Embedding).filter(knowledge_id__in=knowledge_id_list, is_active=True)
    
    for search_handle in search_handle_list:
        if search_handle.support(search_mode):
            return search_handle.handle(query_set, query_text, embedding_query, 
                                       top_number, similarity, search_mode)
```
</augment_code_snippet>

---

## 📋 方式二：问题生成（Problem Generation）- 可选

### 2.1 功能说明

**问题生成**是一个**可选的辅助功能**，用于：
- 基于文档段落自动生成测试问题
- 建立问题与段落的关联关系
- 用于批量测试和评估

**注意**: 这是一个**独立的功能**，不是检索测试的前置条件！

### 2.2 使用场景

适用于：
- ✅ 需要批量生成测试集
- ✅ 建立问题-答案对（QA Pairs）
- ✅ 自动化评估流程

**不适用于**：
- ❌ 日常检索测试（用Hit Test更快）
- ❌ 实时调试检索参数
- ❌ 快速验证检索效果

### 2.3 代码位置

<augment_code_snippet path="apps/knowledge/task/generate.py" mode="EXCERPT">
```python
def generate_problem_by_paragraph(paragraph, llm_model, prompt):
    # 使用LLM基于段落内容生成问题
    res = llm_model.invoke([HumanMessage(
        content=prompt.replace('{data}', paragraph.content)
                     .replace('{title}', paragraph.title)
    )])
    problems = res.content.split('\n')
    for problem in problems:
        save_problem(paragraph.knowledge_id, paragraph.document_id, 
                    paragraph.id, problem)
```
</augment_code_snippet>

---

## 🆚 两种方式对比

| 维度 | 命中测试（Hit Test） | 问题生成（Problem Generation） |
|------|---------------------|------------------------------|
| **依赖关系** | ✅ 完全独立 | ⚠️ 需要LLM模型 |
| **使用场景** | 实时检索测试 | 批量生成测试集 |
| **速度** | ⚡ 即时响应 | 🐌 需要LLM推理 |
| **成本** | 💰 免费（仅向量计算） | 💰💰 消耗LLM Token |
| **灵活性** | ✅ 可自由输入任何问题 | ⚠️ 受限于生成质量 |
| **适用阶段** | 开发、测试、生产 | 主要用于测试准备 |

---

## 🧪 召回率测试最佳实践

### 方法1: 使用Hit Test进行人工评估

```python
# 准备测试问题集
test_queries = [
    "如何提升RAG系统的召回率？",
    "什么是混合检索？",
    "Reranker的作用是什么？"
]

# 对每个问题进行测试
for query in test_queries:
    # 调用Hit Test API
    results = hit_test(query, top_n=10, similarity=0.6, search_mode='blend')
    
    # 人工评估：检查前10个结果中有多少是相关的
    relevant_count = count_relevant_results(results)
    recall = relevant_count / total_relevant_docs
    
    print(f"Query: {query}")
    print(f"Recall@10: {recall:.2%}")
```

### 方法2: 使用标注数据集

```python
# 准备标注数据（问题 -> 相关段落ID列表）
ground_truth = {
    "如何提升召回率？": ["para_id_1", "para_id_2", "para_id_5"],
    "什么是混合检索？": ["para_id_3", "para_id_7"],
}

# 计算召回率
for query, relevant_ids in ground_truth.items():
    results = hit_test(query, top_n=10)
    retrieved_ids = [r['paragraph_id'] for r in results]
    
    # 计算召回率
    hits = len(set(retrieved_ids) & set(relevant_ids))
    recall = hits / len(relevant_ids)
    
    print(f"Recall@10: {recall:.2%}")
```

### 方法3: A/B测试不同参数

```python
# 测试不同的检索模式
modes = ['embedding', 'keywords', 'blend']
results = {}

for mode in modes:
    results[mode] = hit_test(
        query="测试问题",
        search_mode=mode,
        top_n=5,
        similarity=0.7
    )
    
# 对比结果质量
compare_results(results)
```

---

## 📊 评估指标

### 可以直接通过Hit Test计算的指标

1. **Recall@K** (召回率)
   - 前K个结果中包含的相关文档比例
   - 需要人工标注或预定义相关文档

2. **Precision@K** (精确率)
   - 前K个结果中相关文档的比例

3. **MRR** (Mean Reciprocal Rank)
   - 第一个相关结果的排名倒数

4. **NDCG@K** (归一化折损累积增益)
   - 考虑排序质量的综合指标

### 示例代码

```python
def calculate_recall_at_k(query, relevant_ids, k=10):
    """计算Recall@K"""
    results = hit_test(query, top_n=k)
    retrieved_ids = [r['paragraph_id'] for r in results]
    
    hits = len(set(retrieved_ids) & set(relevant_ids))
    recall = hits / len(relevant_ids) if relevant_ids else 0
    
    return recall

def calculate_precision_at_k(query, relevant_ids, k=10):
    """计算Precision@K"""
    results = hit_test(query, top_n=k)
    retrieved_ids = [r['paragraph_id'] for r in results]
    
    hits = len(set(retrieved_ids) & set(relevant_ids))
    precision = hits / k if k > 0 else 0
    
    return precision
```

---

## 🎯 总结

### ✅ 关键要点

1. **Hit Test是独立功能** - 不需要问题生成就能测试检索
2. **问题生成是可选的** - 仅用于批量生成测试集
3. **Hit Test更适合日常测试** - 快速、灵活、免费
4. **可以自己准备测试集** - 人工标注或使用现有数据

### 🚀 推荐流程

```
1. 使用Hit Test进行快速测试
   ↓
2. 准备少量高质量测试问题（10-50个）
   ↓
3. 人工标注相关段落
   ↓
4. 计算召回率、精确率等指标
   ↓
5. 调整参数，重复测试
   ↓
6. （可选）使用问题生成扩充测试集
```

---

**结论**: MaxKB的检索测试**完全不依赖问题生成**，Hit Test功能已经足够强大！🎉

