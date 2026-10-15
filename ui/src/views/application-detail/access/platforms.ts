/** 发布渠道的展示信息、配置字段与平台后台指引。 */
import { APPLICATION_ACCESS_PLATFORM } from '@/api/enums'
import type { ApplicationAccessPlatform } from '@/api/types'
import wecomBotLogo from '@/assets/logo/logo_enterprise-wechat-bot.svg'
import wecomLogo from '@/assets/logo/logo_enterprise-wechat.svg'
import dingtalkLogo from '@/assets/logo/logo_dingtalk.svg'
import wechatLogo from '@/assets/logo/logo_wechat.svg'
import larkLogo from '@/assets/logo/logo_lark.svg'
import slackLogo from '@/assets/logo/logo_slack.svg'

interface AccessField {
  key: string
  label: string
  secret?: boolean
  required?: boolean
}

export interface AccessPlatformDefinition {
  key: ApplicationAccessPlatform
  name: string
  logo: string
  description: string
  fields: AccessField[]
  consoleUrl?: string
  consoleName?: string
  callbackTip?: string
}

export const accessPlatforms: AccessPlatformDefinition[] = [
  {
    key: APPLICATION_ACCESS_PLATFORM.WECOM_BOT,
    name: '企业微信智能机器人',
    logo: wecomBotLogo,
    description: '打造企业微信智能机器人',
    fields: [
      { key: 'token', label: 'Token' },
      { key: 'encoding_aes_key', label: 'EncodingAESKey' },
    ],
    consoleUrl: 'https://work.weixin.qq.com/wework_admin/frame#/manageTools',
    consoleName: '企业微信后台',
    callbackTip: '-管理工具-智能机器人-创建机器人-API模式创建的 "URL" 中',
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.WECOM,
    name: '企业微信应用',
    logo: wecomLogo,
    description: '打造企业微信智能体',
    fields: [
      { key: 'app_id', label: '企业 ID' },
      { key: 'agent_id', label: 'Agent ID' },
      { key: 'secret', label: 'Secret', secret: true },
      { key: 'token', label: 'Token' },
      { key: 'encoding_aes_key', label: 'EncodingAESKey' },
    ],
    consoleUrl: 'https://work.weixin.qq.com/wework_admin/frame#apps',
    consoleName: '企业微信后台',
    callbackTip: '-应用管理-自建-创建的应用-接收消息-设置 API 接收的 "URL" 中',
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.DINGTALK,
    name: '钉钉应用',
    logo: dingtalkLogo,
    description: '打造钉钉智能体',
    fields: [
      { key: 'client_id', label: 'Client ID' },
      { key: 'client_secret', label: 'Client Secret', secret: true },
    ],
    consoleUrl: 'https://open-dev.dingtalk.com/fe/app?hash=%23%2Fcorp%2Fapp#/corp/app',
    consoleName: '钉钉开放平台',
    callbackTip: '-机器人页面，设置 "消息接收模式" 为 HTTP模式 ，并把上面 URL 填写到"消息接收地址"中',
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.WECHAT,
    name: '公众号',
    logo: wechatLogo,
    description: '打造公众号智能体',
    fields: [
      { key: 'app_id', label: '开发者 ID (APP ID)' },
      { key: 'app_secret', label: '开发者密钥 (APP SECRET)', secret: true },
      { key: 'token', label: '令牌 (TOKEN)' },
      { key: 'encoding_aes_key', label: '消息加解密密钥' },
    ],
    consoleUrl: 'https://mp.weixin.qq.com/advanced/advanced?action=dev&t=advanced/dev',
    consoleName: '微信公众平台',
    callbackTip: '-设置与开发-基本配置-服务器配置的 "服务器地址URL" 中',
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.LARK,
    name: '飞书应用',
    logo: larkLogo,
    description: '打造飞书智能体',
    fields: [
      { key: 'app_id', label: 'App ID' },
      { key: 'app_secret', label: 'App Secret', secret: true },
      { key: 'verification_token', label: 'Verification Token', required: false },
    ],
    consoleUrl: 'https://open.feishu.cn/app/',
    consoleName: '飞书开放平台',
    callbackTip: '-事件与回调-事件配置-配置订阅方式的 "请求地址" 中',
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.SLACK,
    name: 'Slack',
    logo: slackLogo,
    description: '打造 Slack 智能体',
    fields: [
      { key: 'signing_secret', label: 'Signing Secret', secret: true },
      { key: 'bot_user_token', label: 'Bot User Token', secret: true },
    ],
  },
]
