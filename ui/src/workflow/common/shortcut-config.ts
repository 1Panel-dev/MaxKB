/**
 * 快捷键配置模块
 * 定义所有可配置动作的默认键位，支持用户通过 localStorage 自定义覆盖
 */

export interface ShortcutBinding {
  /** Mousetrap 格式的键位列表，如 ['ctrl + s', 'cmd + s'] */
  keys: string[]
  /** 显示名称 */
  label: string
  /** i18n key — 用于动态读取翻译 */
  labelKey: string
  /** 分组 */
  group: 'general' | 'edit' | 'view'
}

const STORAGE_KEY = 'workflowShortcuts'

const ALL_ACTIONS: Record<string, ShortcutBinding> = {
  save: { keys: ['cmd + s', 'ctrl + s'], label: '保存', labelKey: 'common.save', group: 'general' },
  debug: { keys: ['cmd + shift + d', 'ctrl + shift + d'], label: '调试', labelKey: 'common.debug', group: 'general' },
  publish: { keys: ['cmd + shift + p', 'ctrl + shift + p'], label: '发布', labelKey: 'common.publish', group: 'general' },
  search: { keys: ['cmd + f', 'ctrl + f'], label: '搜索节点', labelKey: 'workflow.tip.searchPlaceholder', group: 'general' },
  undo: { keys: ['cmd + z', 'ctrl + z'], label: '撤销', labelKey: 'workflow.shortcut.undo', group: 'edit' },
  redo: { keys: ['cmd + y', 'ctrl + y'], label: '重做', labelKey: 'workflow.shortcut.redo', group: 'edit' },
  copy: { keys: ['cmd + c', 'ctrl + c'], label: '复制', labelKey: 'workflow.shortcut.copy', group: 'edit' },
  paste: { keys: ['cmd + v', 'ctrl + v'], label: '粘贴', labelKey: 'workflow.shortcut.paste', group: 'edit' },
  delete: { keys: ['backspace', 'del', 'delete'], label: '删除', labelKey: 'workflow.shortcut.delete', group: 'edit' },
  selectMode: { keys: ['s'], label: '框选模式', labelKey: 'workflow.control.dragMode', group: 'view' },
  handMode: { keys: ['h'], label: '点选模式', labelKey: 'workflow.control.clickMode', group: 'view' },
  zoomIn: { keys: ['cmd + =', 'ctrl + ='], label: '放大', labelKey: 'workflow.control.zoomIn', group: 'view' },
  zoomOut: { keys: ['cmd + -', 'ctrl + -'], label: '缩小', labelKey: 'workflow.control.zoomOut', group: 'view' },
  fitView: { keys: ['cmd + 0', 'ctrl + 0'], label: '适应画布', labelKey: 'workflow.control.fitView', group: 'view' },
  collapseAll: { keys: ['cmd + [', 'ctrl + ['], label: '收起全部', labelKey: 'workflow.control.retract', group: 'view' },
  expandAll: { keys: ['cmd + ]', 'ctrl + ]'], label: '展开全部', labelKey: 'workflow.control.extend', group: 'view' },
  beautify: { keys: ['cmd + shift + l', 'ctrl + shift + l'], label: '一键美化', labelKey: 'workflow.control.beautify', group: 'view' },
}

function loadOverrides(): Record<string, string[]> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

/** 获取某个动作的键位列表（含用户自定义覆盖） */
export function getShortcutKeys(action: string): string[] {
  const overrides = loadOverrides()
  const binding = ALL_ACTIONS[action]
  if (!binding) return []
  if (action in overrides) return overrides[action]
  return binding.keys
}

/** 设置用户自定义键位 */
export function setShortcutKeys(action: string, keys: string[]): void {
  const overrides = loadOverrides()
  overrides[action] = keys
  localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides))
}

/** 重置某个动作为默认键位 */
export function resetShortcutKeys(action: string): void {
  const overrides = loadOverrides()
  delete overrides[action]
  localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides))
}

/** 重置所有动作为默认键位 */
export function resetAllShortcutKeys(): void {
  localStorage.removeItem(STORAGE_KEY)
}

/** 获取所有动作及其当前键位（含用户自定义） */
export function getAllShortcuts(): Record<string, ShortcutBinding> {
  const overrides = loadOverrides()
  const result: Record<string, ShortcutBinding> = {}
  for (const [action, binding] of Object.entries(ALL_ACTIONS)) {
    result[action] = {
      ...binding,
      keys: action in overrides ? overrides[action] : binding.keys,
    }
  }
  return result
}

/** 将 Mousetrap 键位格式转为人类可读的显示文本 */
export function formatKeysForDisplay(keys: string[]): string {
  if (keys.length === 0) return ''
  // 取第一个非 alt 的键位作为主要显示（mac / win 取当前平台匹配的）
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
  let key = keys[0]
  // 如果有 cmd 版本的键，Mac 优先取 cmd；Windows 优先取 ctrl
  const cmdKey = keys.find(k => k.includes('cmd'))
  const ctrlKey = keys.find(k => k.includes('ctrl') && !k.includes('cmd'))
  if (isMac && cmdKey) key = cmdKey
  else if (!isMac && ctrlKey) key = ctrlKey

  return key
    .split(' + ')
    .map(part => {
      const p = part.toLowerCase()
      if (p === 'cmd') return isMac ? '⌘' : 'Cmd'
      if (p === 'ctrl') return isMac ? '⌃' : 'Ctrl'
      if (p === 'shift') return isMac ? '⇧' : 'Shift'
      if (p === 'alt') return isMac ? '⌥' : 'Alt'
      if (p === 'backspace') return '⌫'
      if (p === 'del' || p === 'delete') return '⌦'
      if (p === 'return' || p === 'enter') return '↵'
      if (p === 'escape' || p === 'esc') return 'Esc'
      if (p === '=') return '+'
      if (p === '-') return '-'
      if (p === '0') return '0'
      // 格式化单个字母或数字键
      return p.length === 1 ? p.toUpperCase() : p.charAt(0).toUpperCase() + p.slice(1)
    })
    .join(isMac ? '' : '+')
}
