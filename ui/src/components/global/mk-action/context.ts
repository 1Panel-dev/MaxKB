/** 表格操作与菜单共享的展示上下文。 */
import type { InjectionKey, Ref } from 'vue'

export interface ActionContext {
  display: 'button' | 'menu'
  first?: boolean
}

export const actionContextKey: InjectionKey<Readonly<Ref<ActionContext>>> = Symbol('action-context')
