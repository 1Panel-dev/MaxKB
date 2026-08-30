/** 提供跨页面复用的数字转换和格式化函数。 */

type NullableNumber = number | null | undefined

const FILE_SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB'] as const

/** 按 1024 进位格式化文件大小，单位范围为 `B` 至 `TB`。 */
export function formatFileSize(bytes: NullableNumber): string {
  if (typeof bytes !== 'number' || !Number.isFinite(bytes) || bytes <= 0) return '0 B'

  let normalizedSize = bytes
  let unitIndex = 0

  while (normalizedSize >= 1024 && unitIndex < FILE_SIZE_UNITS.length - 1) {
    normalizedSize /= 1024
    unitIndex += 1
  }

  const formattedSize = unitIndex === 0 ? Math.round(normalizedSize) : Number(normalizedSize.toFixed(1))
  return `${formattedSize} ${FILE_SIZE_UNITS[unitIndex]}`
}

/** 为数字添加千位分隔符，空值按 `0` 处理。 */
export function toThousands(value: NullableNumber | string): string {
  return String(value ?? 0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/** 格式化数量：千以内显示原值，千及以上缩写为一位小数的 `k`。 */
export function numberFormat(value: NullableNumber): string {
  const normalizedValue = value ?? 0

  return normalizedValue < 1000 ? toThousands(normalizedValue) : `${toThousands((normalizedValue / 1000).toFixed(1))}k`
}

/** 将有限数字缩写为最多带一位小数的 `K`、`M`、`B` 或 `T`，空值和无效数字返回 `-`。 */
const TOKEN_NUMBER_UNITS = ['', 'K', 'M', 'B', 'T'] as const
export function formatTokenNumber(value: NullableNumber): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '-'

  let compactValue = value
  let unitIndex = 0

  while (Math.abs(compactValue) >= 1000 && unitIndex < TOKEN_NUMBER_UNITS.length - 1) {
    compactValue /= 1000
    unitIndex += 1
  }

  if (unitIndex === 0) return String(Math.round(compactValue))
  return `${compactValue.toFixed(1)}${TOKEN_NUMBER_UNITS[unitIndex]}`
}
