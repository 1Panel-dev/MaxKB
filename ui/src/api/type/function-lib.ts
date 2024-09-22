interface functionLibData {
  id?: String
  name?: String
  desc?: String
  code?: String
  permission_type?: 'PRIVATE' | 'PUBLIC'
  input_field_list?: Array<any>
  is_active?: Boolean
}

export type { functionLibData }
