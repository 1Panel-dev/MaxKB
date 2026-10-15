/** 后端智能体类型枚举值。 */
export const APPLICATION_TYPE = { SIMPLE: 'SIMPLE', WORK_FLOW: 'WORK_FLOW' } as const

/** 智能体发布渠道的后端平台标识。 */
export const APPLICATION_ACCESS_PLATFORM = {
  WECOM_BOT: 'wecomBot',
  WECOM: 'wecom',
  DINGTALK: 'dingtalk',
  WECHAT: 'wechat',
  LARK: 'lark',
  SLACK: 'slack',
} as const
