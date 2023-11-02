interface datasetListRequest {
  current_page: number
  page_size: number
  search_text: string
}

interface datasetData {
  name: String
  desc: String
  documents?: Array<any>
}

export type { datasetListRequest, datasetData }
