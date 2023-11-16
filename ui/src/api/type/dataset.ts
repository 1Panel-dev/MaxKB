interface datasetListRequest {
  current_page: number
  page_size: number
  name: string
}

interface datasetData {
  name: String
  desc: String
  documents?: Array<any>
}

export type { datasetListRequest, datasetData }
