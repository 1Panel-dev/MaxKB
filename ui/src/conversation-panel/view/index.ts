import { computed, inject, toValue, type InjectionKey, type MaybeRefOrGetter, type Ref } from 'vue'
import type { ChatUserProfile } from '@/api/types'
import type { SidePanelMode } from '../core/layout/types'

export const VIEW_TYPE = {
  CHAT: 'CHAT',
  DEBUG: 'DEBUG',
  SIMPLE_DEBUG: 'SIMPLE_DEBUG',
  PORTAL: 'PORTAL',
  LOG: 'LOG',
} as const
export type ViewType = (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE]

export const VIEW_KEY: InjectionKey<ViewType> = Symbol('conversation-view')

export function useViewType(): ViewType {
  const type = inject(VIEW_KEY)
  if (!type) throw new Error('useViewType 必须在 conversation view 内使用')
  return type
}

/** 对话面板设备类型；平板暂未区分。 */
export const DEVICE_TYPE = {
  PC: 'PC',
  MOBILE: 'MOBILE',
  TABLET: 'TABLET',
} as const
export type DeviceType = (typeof DEVICE_TYPE)[keyof typeof DEVICE_TYPE]

export const DEVICE_KEY: InjectionKey<Readonly<Ref<DeviceType>>> = Symbol('conversation-device')

/** 由左栏模式推导设备类型：左栏为抽屉即手机端，否则为 PC 端。 */
export function createDeviceType(leftMode: MaybeRefOrGetter<SidePanelMode>): Readonly<Ref<DeviceType>> {
  return computed(() => (toValue(leftMode) === 'drawer' ? DEVICE_TYPE.MOBILE : DEVICE_TYPE.PC))
}

export function useDeviceType(): Readonly<Ref<DeviceType>> {
  const device = inject(DEVICE_KEY)
  if (!device) throw new Error('useDeviceType 必须在 conversation view 内使用')
  return device
}

/** HTML 内容 iframe 内 chatUserProfile() 的数据来源；仅 Chat 入口提供，Admin 调试、日志拿到 null。 */
export type GetChatUserProfile = () => Promise<ChatUserProfile | null>

export const CHAT_USER_PROFILE_KEY: InjectionKey<GetChatUserProfile> = Symbol('chat-user-profile')

export function useChatUserProfileGetter(): GetChatUserProfile {
  return inject(CHAT_USER_PROFILE_KEY, () => Promise.resolve(null))
}
