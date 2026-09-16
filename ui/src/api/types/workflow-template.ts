/** 工作流模板中心的模板及下载元数据。 */
export interface WorkflowStoreTemplate {
  id: string
  name: string
  desc?: string | null
  description?: string | null
  icon?: string
  label?: string | null
  downloads?: number
  readMe?: string
  downloadUrl?: string
  downloadCallbackUrl?: string
  [key: string]: unknown
}
