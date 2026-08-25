/** 提供跨页面复用的数字转换和格式化函数。 */

type NullableNumber = number | null | undefined

/** 为数字添加千位分隔符，空值按 `0` 处理。 */
export function toThousands(value: NullableNumber | string): string {
  return String(value ?? 0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/** 格式化数量：千以内显示原值，千及以上缩写为一位小数的 `k`。 */
export function numberFormat(value: NullableNumber): string {
  const normalizedValue = value ?? 0

  return normalizedValue < 1000
    ? toThousands(normalizedValue)
    : `${toThousands((normalizedValue / 1000).toFixed(1))}k`
}
