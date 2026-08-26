/** 对话用户 Token 配额模式枚举值；新增或修改配额模式时以此处为唯一数据源。 */
export const QUOTA_TYPE = {
  UNLIMITED: 'UNLIMITED',
  PERIODIC: 'PERIODIC',
} as const

/** 对话用户 Token 配额周期单位枚举值；新增或修改周期单位时以此处为唯一数据源。 */
export const PERIOD_TYPE = {
  DAY: 'DAY',
  WEEK: 'WEEK',
  MONTH: 'MONTH',
} as const
