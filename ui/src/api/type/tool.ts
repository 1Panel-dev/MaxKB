interface toolData {
  id?: string
  name?: string
  icon?: string
  desc?: string
  code?: string
  input_field_list?: Array<any>
  init_field_list?: Array<any>
  is_active?: boolean
  folder_id?: string
  tool_type?: string
}

interface AddInternalToolParam {
  name: string,
  folder_id: string
}

export type { toolData, AddInternalToolParam }
