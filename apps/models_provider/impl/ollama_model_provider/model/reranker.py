from typing import Sequence, Optional, Dict

from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document
from pydantic import BaseModel, Field

from models_provider.base_model_provider import MaxKBBaseModel


class OllamaReranker(MaxKBBaseModel, OllamaEmbeddings, BaseModel):
    top_n: Optional[int] = Field(3, description="Number of top documents to return")

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return OllamaReranker(
            model=model_name,
            base_url=model_credential.get('api_base'),
            **optional_params
        )

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        from sklearn.metrics.pairwise import cosine_similarity
        """Rank documents based on their similarity to the query.

              Args:
                  query: The query text.
                  documents: The list of document texts to rank.

              Returns:
                  List of documents sorted by relevance to the query.
              """
        # 获取查询和文档的嵌入
        query_embedding = self.embed_query(query)
        documents = [doc.page_content for doc in documents]
        document_embeddings = self.embed_documents(documents)
        # 计算相似度
        similarities = cosine_similarity([query_embedding], document_embeddings)[0]
        ranked_docs = [(doc, _) for _, doc in sorted(zip(similarities, documents), reverse=True)][:self.top_n]
        return [
            Document(
                page_content=doc,  # 第一个值是文档内容
                metadata={'relevance_score': score}  # 第二个值是相似度分数
            )
            for doc, score in ranked_docs
        ]
