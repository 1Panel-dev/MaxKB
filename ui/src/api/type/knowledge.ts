interface knowledgeData {
  name: String
  desc: String
  documents?: Array<any>
  type?: String
  embedding_model_id?: String
}

export type { knowledgeData }
