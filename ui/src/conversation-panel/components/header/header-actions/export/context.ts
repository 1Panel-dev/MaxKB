import type { InjectionKey } from 'vue'

/** 当前主面板的消息正文，由主面板提供，避免读取其他对话或调试窗口。 */
export const EXPORT_MESSAGE_ELEMENT_KEY: InjectionKey<() => HTMLElement | null> = Symbol('export-message-element')
