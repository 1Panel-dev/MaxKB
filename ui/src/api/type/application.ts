interface ApplicationFormType {
  name?: string
  desc?: string
  model_id: string
  multiple_rounds_dialogue: boolean
  prologue?: string
  example?: string[]
  dataset_id_list: string[]
}
export type { ApplicationFormType }
