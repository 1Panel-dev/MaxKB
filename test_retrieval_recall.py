#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MaxKB检索召回率测试脚本
使用Hit Test功能测试检索质量，无需依赖问题生成

使用方法:
    python test_retrieval_recall.py --knowledge-id <知识库ID>
    python test_retrieval_recall.py --knowledge-id <知识库ID> --test-file test_queries.json
"""
import sys
import os
import django
import json
from typing import List, Dict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
django.setup()

from knowledge.models import Knowledge
from knowledge.serializers.knowledge import KnowledgeSerializer
from common.config.embedding_config import VectorStore
from knowledge.serializers.common import get_embedding_model_by_knowledge_id

def hit_test(knowledge_id: str, query_text: str, top_n: int = 10, 
             similarity: float = 0.6, search_mode: str = 'blend') -> List[Dict]:
    """
    执行命中测试
    
    Args:
        knowledge_id: 知识库ID
        query_text: 查询文本
        top_n: 返回结果数量
        similarity: 相似度阈值
        search_mode: 检索模式 (embedding/keywords/blend)
    
    Returns:
        检索结果列表
    """
    try:
        result = KnowledgeSerializer.HitTest(
            data={
                'knowledge_id': knowledge_id,
                'query_text': query_text,
                'top_number': top_n,
                'similarity': similarity,
                'search_mode': search_mode
            }
        ).hit_test()
        return result
    except Exception as e:
        print(f"❌ 检索失败: {str(e)}")
        return []

def calculate_recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int = 10) -> float:
    """计算Recall@K"""
    if not relevant_ids:
        return 0.0
    
    retrieved_set = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    
    hits = len(retrieved_set & relevant_set)
    recall = hits / len(relevant_set)
    
    return recall

def calculate_precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int = 10) -> float:
    """计算Precision@K"""
    if k == 0:
        return 0.0
    
    retrieved_set = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    
    hits = len(retrieved_set & relevant_set)
    precision = hits / k
    
    return precision

def calculate_mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    """计算Mean Reciprocal Rank"""
    relevant_set = set(relevant_ids)
    
    for i, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_set:
            return 1.0 / i
    
    return 0.0

def run_test_suite(knowledge_id: str, test_cases: List[Dict], search_mode: str = 'blend'):
    """
    运行测试套件
    
    Args:
        knowledge_id: 知识库ID
        test_cases: 测试用例列表，格式:
            [
                {
                    "query": "测试问题",
                    "relevant_paragraph_ids": ["para_id_1", "para_id_2"]
                },
                ...
            ]
        search_mode: 检索模式
    """
    print("="*80)
    print(f"MaxKB检索召回率测试")
    print(f"知识库ID: {knowledge_id}")
    print(f"检索模式: {search_mode}")
    print(f"测试用例数: {len(test_cases)}")
    print("="*80)
    
    total_recall_5 = 0
    total_recall_10 = 0
    total_precision_5 = 0
    total_precision_10 = 0
    total_mrr = 0
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case['query']
        relevant_ids = test_case['relevant_paragraph_ids']
        
        print(f"\n[{i}/{len(test_cases)}] 测试: {query}")
        print(f"  相关段落数: {len(relevant_ids)}")
        
        # 执行检索
        results = hit_test(knowledge_id, query, top_n=10, search_mode=search_mode)
        retrieved_ids = [r['paragraph_id'] for r in results]
        
        # 计算指标
        recall_5 = calculate_recall_at_k(retrieved_ids, relevant_ids, k=5)
        recall_10 = calculate_recall_at_k(retrieved_ids, relevant_ids, k=10)
        precision_5 = calculate_precision_at_k(retrieved_ids, relevant_ids, k=5)
        precision_10 = calculate_precision_at_k(retrieved_ids, relevant_ids, k=10)
        mrr = calculate_mrr(retrieved_ids, relevant_ids)
        
        total_recall_5 += recall_5
        total_recall_10 += recall_10
        total_precision_5 += precision_5
        total_precision_10 += precision_10
        total_mrr += mrr
        
        print(f"  Recall@5:     {recall_5:.2%}")
        print(f"  Recall@10:    {recall_10:.2%}")
        print(f"  Precision@5:  {precision_5:.2%}")
        print(f"  Precision@10: {precision_10:.2%}")
        print(f"  MRR:          {mrr:.3f}")
        
        # 显示检索结果
        if results:
            print(f"  前3个结果:")
            for j, r in enumerate(results[:3], 1):
                is_relevant = "✓" if r['paragraph_id'] in relevant_ids else "✗"
                print(f"    {j}. [{is_relevant}] {r.get('title', 'N/A')[:50]}... (相似度: {r.get('similarity', 0):.3f})")
    
    # 输出平均指标
    n = len(test_cases)
    print("\n" + "="*80)
    print("📊 平均指标:")
    print("="*80)
    print(f"Recall@5:     {total_recall_5/n:.2%}")
    print(f"Recall@10:    {total_recall_10/n:.2%}")
    print(f"Precision@5:  {total_precision_5/n:.2%}")
    print(f"Precision@10: {total_precision_10/n:.2%}")
    print(f"MRR:          {total_mrr/n:.3f}")
    print("="*80)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MaxKB检索召回率测试')
    parser.add_argument('--knowledge-id', required=True, help='知识库ID')
    parser.add_argument('--test-file', help='测试用例JSON文件路径')
    parser.add_argument('--search-mode', default='blend', choices=['embedding', 'keywords', 'blend'], 
                       help='检索模式')
    
    args = parser.parse_args()
    
    # 加载测试用例
    if args.test_file:
        with open(args.test_file, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    else:
        # 使用示例测试用例
        print("⚠️  未指定测试文件，使用示例测试用例")
        print("💡 提示: 创建test_queries.json文件来定义自己的测试用例\n")
        test_cases = [
            {
                "query": "示例问题1",
                "relevant_paragraph_ids": []  # 需要手动填写相关段落ID
            }
        ]
    
    # 运行测试
    run_test_suite(args.knowledge_id, test_cases, args.search_mode)

if __name__ == "__main__":
    main()

