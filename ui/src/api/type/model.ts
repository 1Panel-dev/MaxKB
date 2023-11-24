interface modelRequest {
  name: string
  model_type: string
  model_name: string
}

interface Provider {
  /**
   * 供应商代号
   */
  provider: string
  /**
   * 供应商名称
   */
  name: string
  /**
   * 供应商icon
   */
  icon: string
}

export type { modelRequest, Provider }
