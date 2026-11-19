/** 发布渠道的展示信息、配置字段与平台后台指引。 */
import { computed, reactive } from 'vue'
import type { ApplicationAccessPlatform } from '@/api/types'
import { APPLICATION_ACCESS_PLATFORM } from '@/api/enums'
import dingtalkLogo from '@/assets/logo/logo_dingtalk.svg'
import wecomBotLogo from '@/assets/logo/logo_enterprise-wechat-bot.svg'
import wecomLogo from '@/assets/logo/logo_enterprise-wechat.svg'
import larkLogo from '@/assets/logo/logo_lark.svg'
import slackLogo from '@/assets/logo/logo_slack.svg'
import wechatLogo from '@/assets/logo/logo_wechat.svg'
import { t } from '@/locales'

interface AccessField {
  key: string
  label?: string
  secret?: boolean
  required?: boolean
}

interface AccessModeOption {
  value: string
  label: string
  tip: string
}

export interface AccessPlatformDefinition {
  key: ApplicationAccessPlatform
  logo: string
  fields: AccessField[]
  modeField?: { key: string; default: string; options: AccessModeOption[]; fields?: Partial<Record<string, AccessField[]>> }
  consoleUrl?: string
  consoleName?: string
}

export const accessPlatforms: AccessPlatformDefinition[] = reactive([
  {
    key: APPLICATION_ACCESS_PLATFORM.WECOM_BOT,
    logo: wecomBotLogo,
    fields: [
      { key: 'token', label: 'Token' },
      { key: 'encoding_aes_key', label: 'EncodingAESKey' },
    ],
    modeField: {
      key: 'mode',
      default: 'ws',
      options: [
        {
          value: 'ws',
          label: computed(() => t('application.access.connection.longConnection')),
          tip: computed(() => t('application.access.wecomBot.longConnectionHint')),
        },
        {
          value: 'callback',
          label: computed(() => t('application.access.connection.callback')),
          tip: computed(() => t('application.access.connection.callbackHint')),
        },
      ],
      fields: {
        ws: [
          { key: 'bot_id', label: 'Bot ID' },
          { key: 'secret', label: 'Secret', secret: true },
        ],
        callback: [
          { key: 'token', label: 'Token' },
          { key: 'encoding_aes_key', label: 'EncodingAESKey' },
        ],
      },
    },
    consoleUrl: 'https://work.weixin.qq.com/wework_admin/frame#/manageTools',
    consoleName: computed(() => t('application.access.consoles.wecom')),
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.WECOM,
    logo: wecomLogo,
    fields: [
      { key: 'app_id', label: computed(() => t('application.access.wecom.corporationId')) },
      { key: 'agent_id', label: 'Agent ID' },
      { key: 'secret', label: 'Secret', secret: true },
      { key: 'token', label: 'Token' },
      { key: 'encoding_aes_key', label: 'EncodingAESKey' },
    ],
    consoleUrl: 'https://work.weixin.qq.com/wework_admin/frame#apps',
    consoleName: computed(() => t('application.access.consoles.wecom')),
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.DINGTALK,
    logo: dingtalkLogo,
    fields: [
      { key: 'client_id', label: 'Client ID' },
      { key: 'client_secret', label: 'Client Secret', secret: true },
    ],
    modeField: {
      key: 'mode',
      default: 'stream',
      options: [
        {
          value: 'stream',
          label: computed(() => t('application.access.connection.longConnection')),
          tip: computed(() => t('application.access.dingtalk.longConnectionHint')),
        },
        {
          value: 'callback',
          label: computed(() => t('application.access.connection.callback')),
          tip: computed(() => t('application.access.connection.callbackHint')),
        },
      ],
      fields: {
        stream: [
          { key: 'client_id', label: 'Client ID' },
          { key: 'client_secret', label: 'Client Secret', secret: true },
        ],
        callback: [
          { key: 'client_id', label: 'Client ID' },
          { key: 'client_secret', label: 'Client Secret', secret: true },
        ],
      },
    },
    consoleUrl: 'https://open-dev.dingtalk.com/fe/app?hash=%23%2Fcorp%2Fapp#/corp/app',
    consoleName: computed(() => t('application.access.consoles.dingtalk')),
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.WECHAT,
    logo: wechatLogo,
    fields: [
      { key: 'app_id', label: computed(() => t('application.access.wechat.developerId')) },
      { key: 'app_secret', label: computed(() => t('application.access.wechat.developerSecret')), secret: true },
      { key: 'token', label: computed(() => t('application.access.wechat.token')) },
      { key: 'encoding_aes_key', label: computed(() => t('application.access.wechat.encodingAesKey')) },
    ],
    consoleUrl: 'https://mp.weixin.qq.com/advanced/advanced?action=dev&t=advanced/dev',
    consoleName: computed(() => t('application.access.consoles.wechat')),
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.LARK,
    logo: larkLogo,
    fields: [
      { key: 'app_id', label: 'App ID' },
      { key: 'app_secret', label: 'App Secret', secret: true },
    ],
    modeField: {
      key: 'mode',
      default: 'ws',
      options: [
        {
          value: 'ws',
          label: computed(() => t('application.access.connection.longConnection')),
          tip: computed(() => t('application.access.lark.longConnectionHint')),
        },
        {
          value: 'callback',
          label: computed(() => t('application.access.connection.callback')),
          tip: computed(() => t('application.access.lark.callbackHint')),
        },
      ],
      fields: {
        ws: [
          { key: 'app_id', label: 'App ID' },
          { key: 'app_secret', label: 'App Secret', secret: true },
        ],
        callback: [
          { key: 'app_id', label: 'App ID' },
          { key: 'app_secret', label: 'App Secret', secret: true },
          { key: 'verification_token', label: 'Verification Token', required: true },
        ],
      },
    },
    consoleUrl: 'https://open.feishu.cn/app/',
    consoleName: computed(() => t('application.access.consoles.lark')),
  },
  {
    key: APPLICATION_ACCESS_PLATFORM.SLACK,
    logo: slackLogo,
    fields: [
      { key: 'signing_secret', label: 'Signing Secret', secret: true },
      { key: 'bot_user_token', label: 'Bot User Token', secret: true },
    ],
  },
])
