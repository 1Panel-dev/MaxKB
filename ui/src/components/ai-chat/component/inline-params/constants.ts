/**
 * 用户输入参数平铺白名单
 *
 * 只有这些 input_type 的字段可以被设置为外置参数（在聊天框上平铺显示）。
 * 改动这里会影响 3 个消费方，注意同步语义：
 * - UserInputTitleDialog.vue —— 齿轮弹窗中 select option 的 disabled 判断
 * - inline-params/index.vue  —— 渲染时兜底过滤，防止白名单被绕过
 * - base-node/UserInputFieldTable.vue —— 字段类型变更/删除时清理脏数据
 */
export const ALLOWED_EXPOSED_TYPES = [
  'Model',
  'Knowledge',
  'SwitchInput',
  'DatePicker',
  'TreeSelect',
  'SingleSelect',
  'MultiSelect',
] as const
