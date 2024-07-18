interface datasetData {
  name: String
  desc: String
  documents?: Array<any>
  type?: String
  embedding_mode_id?: String
}

export type { datasetData }
