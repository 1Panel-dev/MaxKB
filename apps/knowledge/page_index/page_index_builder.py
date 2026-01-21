# coding=utf-8
"""
PageIndex树构建器
从文档列表构建层次树结构索引
"""
import re
from typing import List, Dict, Optional
from django.db import transaction

from knowledge.models import Document, Knowledge, PageIndexNode, Paragraph, State
from common.utils.split_model import SplitModel, smart_split_paragraph


class PageIndex:
    """PageIndex层次树索引构建器"""
    
    def __init__(self, knowledge: Knowledge):
        self.knowledge = knowledge
    
    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        knowledge: Knowledge,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> 'PageIndex':
        """
        从文档列表构建PageIndex树
        
        Args:
            documents: 文档列表
            knowledge: 所属知识库
            chunk_size: 章节分块大小（默认1000字符）
            chunk_overlap: 章节重叠大小（默认200字符）
            
        Returns:
            PageIndex实例
        """
        page_index = cls(knowledge)
        page_index.build_tree_from_documents(
            documents, 
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return page_index
    
    def build_tree_from_documents(
        self,
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        从文档列表构建PageIndex树
        
        流程：
        1. 清理现有PageIndex数据
        2. 解析每个文档为树形结构
        3. 创建PageIndexNode记录
        """
        # 构建新树
        for doc in documents:
            with transaction.atomic():
                PageIndexNode.objects.filter(document=doc).delete()
                self._process_single_document(doc, chunk_size, chunk_overlap)
    
    def _process_single_document(
        self,
        document: Document,
        chunk_size: int,
        chunk_overlap: int
    ):
        """处理单个文档"""
        print(f"[PageIndex] Processing document: {document.name} (ID: {document.id})")

        # 1. 从Paragraph表获取文档所有段落内容
        paragraphs = Paragraph.objects.filter(
            document=document,
            is_active=True
        ).order_by('position')

        print(f"[PageIndex] Found {paragraphs.count()} active paragraphs for document: {document.name}")

        # 拼接所有段落内容为完整文档
        document_content = '\n\n'.join([
            para.content for para in paragraphs
        ])

        print(f"[PageIndex] Document content length: {len(document_content)} characters")

        if not document_content:
            print(f"Warning: Document {document.name} has no active paragraphs")
            return

        # 2. 使用SplitModel解析文档树
        split_model = SplitModel(
            content_level_pattern=self._get_markdown_patterns(),
            with_filter=True,
            limit=chunk_size
        )

        tree = []
        try:
            tree = split_model.parse_to_tree(document_content, index=0)
            print(f"[PageIndex] Document tree parsed successfully, root nodes: {len(tree)}")
        except Exception as e:
            print(f"Warning: Failed to parse document tree for {document.name}: {e}")
            print("[PageIndex] Document may not have Markdown titles (#, ##, ###), creating root node only")

        has_title = any(item.get('state') == 'title' for item in tree)

        # 3. 创建根节点（无论是否解析成功，都创建根节点）
        root_content = document_content[:chunk_size] if has_title else ''
        root_node = self._create_node(
            document=document,
            level=0,
            title=document.name,
            path=[document.name],
            content=root_content,
            parent=None,
            order=0
        )

        print(f"[PageIndex] Root node created: {root_node.id}")

        # 4. 解析成功时递归创建子节点
        if tree and has_title:
            self._create_nodes_from_tree(
                tree=tree,
                document=document,
                parent=root_node,
                current_path=[document.name],
                chunk_size=chunk_size
            )
        else:
            block_list = []
            if tree:
                block_list = [item for item in tree if item.get('state') == 'block']
            if not block_list:
                block_list = [
                    {'state': 'block', 'content': block}
                    for block in smart_split_paragraph(document_content, limit=chunk_size)
                ]

            for idx, block in enumerate(block_list):
                block_content = block.get('content', '')
                if not block_content.strip():
                    continue

                block_title = f"Chunk {idx + 1}"
                self._create_node(
                    document=document,
                    level=1,
                    title=block_title,
                    path=[document.name, block_title],
                    content=block_content,
                    parent=root_node,
                    order=idx
                )

            print(f"[PageIndex] No title structure found, created {len(block_list)} chunk nodes")

        # 4. 【新增】调度异步向量化任务（事务提交后执行，避免读取不到节点）
        try:
            from knowledge.tasks import generate_page_index_embeddings

            def _schedule_embedding():
                generate_page_index_embeddings.delay(str(document.id))
                print(f"[PageIndex] Async embedding task scheduled for document: {document.id}")

            transaction.on_commit(_schedule_embedding)
        except ImportError:
            print("[PageIndex] Warning: Celery not available, embedding not scheduled")
        except Exception as e:
            print(f"[PageIndex] Error scheduling embedding: {e}")

        print(f"[PageIndex] Document processing completed: {document.name}")
    
    def _create_nodes_from_tree(
        self,
        tree: List[Dict],
        document: Document,
        parent: PageIndexNode,
        current_path: List[str],
        chunk_size: int
    ):
        """从树结构递归创建节点"""
        for idx, item in enumerate(tree):
            item_path = current_path + [item['content']]
            
            if item['state'] == 'title':
                # 创建章节节点
                node = self._create_node(
                    document=document,
                    level=len(item_path) - 1,
                    title=item['content'],
                    path=item_path,
                    content=self._extract_node_content(item, chunk_size),
                    parent=parent,
                    order=idx
                )
                
                # 递归处理子节点
                children = item.get('children', [])
                if children:
                    self._create_nodes_from_tree(
                        children, document, node, item_path, chunk_size
                    )
            
            elif item['state'] == 'block' and parent:
                # 内容块：添加到父节点
                if parent.content:
                    parent.content += "\n\n"
                parent.content += item['content']
                parent.char_count = len(parent.content)
                parent.save()
    
    def _create_node(
        self,
        document: Document,
        level: int,
        title: str,
        path: List[str],
        content: str,
        parent: Optional[PageIndexNode] = None,
        order: int = 0
    ) -> PageIndexNode:
        """创建PageIndexNode记录"""
        return PageIndexNode.objects.create(
            document=document,
            knowledge=self.knowledge,
            level=level,
            title=title,
            path=path,
            parent=parent,
            order=order,
            content=content,
            char_count=len(content),
            embedding_status=State.PENDING.value
        )
    
    def _extract_node_content(self, item: Dict, chunk_size: int) -> str:
        """提取节点内容"""
        content_parts = []
        current_length = 0
        
        # 收集子节点内容
        children = item.get('children', [])
        for child in children:
            if child['state'] == 'block':
                if current_length + len(child['content']) > chunk_size:
                    break
                content_parts.append(child['content'])
                current_length += len(child['content'])
        
        return "\n\n".join(content_parts)
    
    def _get_markdown_patterns(self):
        """获取Markdown标题正则"""
        return [
            re.compile('(?<=^)# .*|(?<=\\n)# .*'),
            re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
            re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
            re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
        ]
    
    def get_tree_summary(self, max_depth: int = 3) -> str:
        """获取树结构摘要"""
        nodes = PageIndexNode.objects.filter(
            knowledge=self.knowledge,
            level__lte=max_depth
        ).order_by('level', 'order')
        
        summary_lines = []
        for node in nodes:
            indent = "  " * node.level
            summary_lines.append(f"{indent}- {node.title}")
        
        return "\n".join(summary_lines)
    
    def get_statistics(self) -> Dict:
        """获取PageIndex统计信息"""
        total_nodes = PageIndexNode.objects.filter(
            knowledge=self.knowledge
        ).count()
        
        depth_stats = {}
        for level in range(0, 10):
            count = PageIndexNode.objects.filter(
                knowledge=self.knowledge,
                level=level
            ).count()
            if count > 0:
                depth_stats[f"level_{level}"] = count
        
        max_depth = 0
        if depth_stats:
            max_depth = max(int(k.split('_')[1]) for k in depth_stats.keys())
        
        return {
            'total_nodes': total_nodes,
            'depth_distribution': depth_stats,
            'max_depth': max_depth
        }
