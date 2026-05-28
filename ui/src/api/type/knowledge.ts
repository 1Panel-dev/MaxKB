interface knowledgeData {
  name: string
  folder_id?: string
  desc: string
  embedding_model_id?: string
  documents?: Array<any>
  vector_store_type?: string
}

export type { knowledgeData }
