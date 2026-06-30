<template>
  <el-dialog
    class="scrollbar-dialog"
    align-center
    :title="$t('workflow.shortcut.title')"
    v-model="dialogVisible"
    width="650px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="shortcut-editor">
      <el-alert
        :title="$t('workflow.shortcut.reloadTip')"
        type="info"
        show-icon
        :closable="false"
        class="mb-16"
      />
      <el-table :data="shortcutList" stripe max-height="480" style="width: 100%">
        <el-table-column :label="$t('workflow.shortcut.action')" min-width="140">
          <template #default="{ row }">
            {{ row.label }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('workflow.shortcut.keys')" min-width="200">
          <template #default="{ row }">
            <div class="flex align-center" style="gap: 6px">
              <el-tag
                v-for="(key, i) in row.displayKeys"
                :key="i"
                size="small"
                :type="row.changed ? 'warning' : ''"
              >
                {{ key }}
              </el-tag>
              <el-tag
                v-if="row.editing"
                ref="recordingRef"
                class="recording-tag"
                size="small"
                type="danger"
              >
                {{ $t('workflow.shortcut.pressKeys') }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('workflow.shortcut.operation')" width="160" align="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.editing"
              text
              size="small"
              @click="startEdit(row)"
            >
              {{ $t('common.edit') }}
            </el-button>
            <template v-else>
              <el-button text size="small" type="primary" @click="confirmEdit(row)">
                {{ $t('common.confirm') }}
              </el-button>
              <el-button text size="small" @click="cancelEdit(row)">
                {{ $t('common.cancel') }}
              </el-button>
            </template>
            <el-button
              v-if="row.changed"
              text
              size="small"
              type="danger"
              @click="resetRow(row)"
            >
              {{ $t('workflow.shortcut.reset') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="resetAll">
          {{ $t('workflow.shortcut.resetAll') }}
        </el-button>
        <el-button type="primary" @click="dialogVisible = false">
          {{ $t('common.close') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onUnmounted, watch } from 'vue'
import { t } from '@/locales'
import {
  getAllShortcuts,
  setShortcutKeys,
  resetShortcutKeys,
  resetAllShortcutKeys,
  formatKeysForDisplay,
} from '@/workflow/common/shortcut-config'
import type { ShortcutBinding } from '@/workflow/common/shortcut-config'

const props = defineProps<{
  visible?: boolean
}>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()
const dialogVisible = ref(false)
watch(() => props.visible, (val) => { dialogVisible.value = val ?? false })
watch(dialogVisible, (val) => emit('update:visible', val))

interface ShortcutRow {
  action: string
  label: string
  keys: string[]
  displayKeys: string[]
  changed: boolean
  editing: boolean
}

const shortcutList = ref<ShortcutRow[]>([])
const recordingRef = ref<HTMLElement>()

/** 正在录制中的 row */
let recordingRow: ShortcutRow | null = null

const keydownHandler = (e: KeyboardEvent) => {
  if (!recordingRow) return
  e.preventDefault()
  e.stopPropagation()

  const parts: string[] = []
  if (e.metaKey) parts.push(isMac ? 'cmd' : 'ctrl')
  if (e.ctrlKey) parts.push('ctrl')
  if (e.altKey) parts.push('alt')
  if (e.shiftKey) parts.push('shift')

  // 排除单独按修饰键
  const key = e.key.toLowerCase()
  const isModifier = ['control', 'shift', 'alt', 'meta'].includes(key)
  if (isModifier && parts.length <= 1) return

  if (!isModifier) {
    // 映射特殊键名到 Mousetrap 格式
    const mappedKey = keyMap(key)
    parts.push(mappedKey)
  }

  if (parts.length === 0) return

  // 转成 Mousetrap 格式
  const shortcut = parts.join(' + ')

  // 更新当前录制的行
  const row = recordingRow
  row.keys = shortcut.includes('cmd') || shortcut.includes('ctrl')
    ? [shortcut]
    : [shortcut, shortcut]  // 单键直接显示
  if (!shortcut.includes('cmd') && !shortcut.includes('ctrl')) {
    row.keys = [shortcut]
  } else if (isMac && shortcut.includes('cmd')) {
    row.keys = [shortcut, shortcut.replace('cmd', 'ctrl')]
  } else if (!isMac && shortcut.includes('ctrl')) {
    row.keys = [shortcut, shortcut.replace('ctrl', 'cmd')]
  } else {
    row.keys = [shortcut]
  }
  row.displayKeys = row.keys.map(k => formatKeysForDisplay([k]))
}

onUnmounted(() => {
  document.removeEventListener('keydown', keydownHandler)
})

function loadList() {
  const data = getAllShortcuts()
  shortcutList.value = Object.entries(data).map(([action, binding]) => ({
    action,
    label: resolveLabel(binding),
    keys: [...binding.keys],
    displayKeys: binding.keys.map(k => formatKeysForDisplay([k])),
    changed: hasOverride(action),
    editing: false,
  }))
}

function hasOverride(action: string): boolean {
  const raw = localStorage.getItem('workflowShortcuts')
  if (!raw) return false
  try {
    const overrides = JSON.parse(raw)
    return action in overrides
  } catch {
    return false
  }
}

function resolveLabel(binding: ShortcutBinding): string {
  // 尝试从 i18n 读取
  const translated = t(binding.labelKey as any)
  return translated && !translated.startsWith('workflow.') ? translated : binding.label
}

function startEdit(row: ShortcutRow) {
  // 取消其它行的编辑
  shortcutList.value.forEach(r => { r.editing = false })
  row.editing = true
  recordingRow = row
  document.addEventListener('keydown', keydownHandler)
}

function confirmEdit(row: ShortcutRow) {
  row.editing = false
  recordingRow = null
  document.removeEventListener('keydown', keydownHandler)
  setShortcutKeys(row.action, row.keys)
  row.changed = hasOverride(row.action)
  row.displayKeys = row.keys.map(k => formatKeysForDisplay([k]))
}

function cancelEdit(row: ShortcutRow) {
  row.editing = false
  recordingRow = null
  document.removeEventListener('keydown', keydownHandler)
  // 恢复原始键位
  const data = getAllShortcuts()
  const original = data[row.action]
  if (original) {
    row.keys = [...original.keys]
    row.displayKeys = original.keys.map(k => formatKeysForDisplay([k]))
  }
}

function resetRow(row: ShortcutRow) {
  resetShortcutKeys(row.action)
  const data = getAllShortcuts()
  const original = data[row.action]
  if (original) {
    row.keys = [...original.keys]
    row.displayKeys = original.keys.map(k => formatKeysForDisplay([k]))
  }
  row.changed = false
}

function resetAll() {
  resetAllShortcutKeys()
  loadList()
}

function keyMap(key: string): string {
  const map: Record<string, string> = {
    ' ': 'space',
    '.': 'period',
    ',': 'comma',
    ';': 'semicolon',
    "'": 'quote',
    '`': 'backquote',
    '[': 'leftbracket',
    ']': 'rightbracket',
    '\\': 'backslash',
    '/': 'slash',
    'escape': 'esc',
    'return': 'enter',
    'delete': 'del',
  }
  return map[key] || key
}

const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0

// 当对话框打开时刷新列表
watch(() => dialogVisible.value, (val) => {
  if (val) loadList()
})
</script>

<style scoped>
.shortcut-editor {
  min-height: 200px;
}
.mb-16 {
  margin-bottom: 16px;
}
.recording-tag {
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
