import mitt, { type Emitter } from 'mitt'

/**
 * 全局事件总线。
 * mk-dynamics-form 用它在字段之间传递「值变化 / 联动触发」事件。
 */
const bus: Emitter<Record<string, unknown>> = mitt<Record<string, unknown>>()

export default bus
