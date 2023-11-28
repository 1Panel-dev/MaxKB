interface ApplicationFormType {
  name?: string
  desc?: string
  model_id: string
  multiple_rounds_dialogue: boolean
  prologue?: string
  example?: string[]
  dataset_id_list: string[]
}
interface chatType {
  id: string
  problem_text: string
  answer_text: string
}
export type { ApplicationFormType, chatType }
