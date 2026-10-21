/** 平台许可证中用于关于弹窗展示的授权信息。 */
export interface LicenseInfo {
  corporation?: string
  expired?: string
  serialNo?: string
  remark?: string
}

export interface LicenseProfile {
  status?: string
  license?: LicenseInfo | null
  message?: string
}
