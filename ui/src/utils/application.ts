export const defaultIcon = '/ui/favicon.ico'

// 是否显示字母 / icon
export function isAppIcon(url: string | undefined) {
  return url === defaultIcon ? '' : url
}

export function isWorkFlow(type: string | undefined) {
  return type === 'WORK_FLOW'
}
