import type { TriggerSetting } from '@/components/dynamics-form/type'

type GetRequest = (url: string, params?: unknown, loading?: any) => Promise<any>

interface TriggerContext {
  triggerValue: any
  otherParams?: Record<string, any>
  loading?: any
  get: GetRequest
}

const LEGACY_CHILDREN_LOADER =
  'self.children=()=>request.get(extra.renderTemplate(trigger_setting.url)).then(ok=>{returnok})'
const UNSAFE_TARGET_FIELDS = new Set(['__proto__', 'prototype', 'constructor'])

export const renderTriggerTemplate = (template: string, data: Record<string, any>) => {
  return template.replace(/\$\{(\w+)\}/g, (match, key) => {
    return data[key] !== undefined ? String(data[key]) : match
  })
}

const getRequestAction = (setting: TriggerSetting) => {
  if (setting.request_action) {
    return setting.request_action
  }
  if (!setting.request) {
    return 'get'
  }
  if (setting.request.replace(/\s/g, '') === LEGACY_CHILDREN_LOADER) {
    return 'set_children_loader'
  }
  return undefined
}

const getResponseValue = (setting: TriggerSetting, response: any) => {
  if (setting.response_type === 'data') {
    return response?.data
  }

  const sharedModels = Array.isArray(response?.data?.shared_model) ? response.data.shared_model : []
  const workspaceModels = Array.isArray(response?.data?.model) ? response.data.model : []
  return [
    ...sharedModels.map((model: any) => ({ ...model, type: 'share' })),
    ...workspaceModels.map((model: any) => ({ ...model, type: 'workspace' })),
  ]
}

const isSafeTargetField = (field: unknown): field is string => {
  return typeof field === 'string' && field.length > 0 && !UNSAFE_TARGET_FIELDS.has(field)
}

export const runTrigger = (setting: TriggerSetting, self: any, context: TriggerContext) => {
  const requestAction = getRequestAction(setting)
  if (!requestAction || !setting.url) {
    return
  }

  const load = () =>
    context.get(
      renderTriggerTemplate(setting.url as string, {
        trigger_value: context.triggerValue,
        ...context.otherParams,
      }),
      {},
      context.loading,
    )

  if (requestAction === 'set_children_loader') {
    self.children = load
    return
  }

  const requestCall = load()
  if (!isSafeTargetField(setting.change_field) || (setting.change && !setting.response_type)) {
    return requestCall
  }

  return requestCall.then((response: any) => {
    self[setting.change_field as string] = getResponseValue(setting, response)
  })
}
