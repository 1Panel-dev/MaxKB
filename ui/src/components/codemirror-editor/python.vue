<script setup lang="ts">
import { ref } from 'vue'
import type { EditorState } from '@codemirror/state'
import { linter, type Diagnostic } from '@codemirror/lint'
import { python } from '@codemirror/lang-python'
import { Codemirror } from 'vue-codemirror'
import ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolPylintIssue } from '@/api/types'

defineOptions({ name: 'PythonCodeEditor', inheritAttrs: false })

const code = defineModel<string>({ required: true })
defineProps<{ title?: string }>()

const emit = defineEmits<{ submitDialog: [code: string] }>()

defineSlots<{ 'header-extra'?(): unknown }>()

function getDocumentPosition(state: EditorState, line: number, column: number) {
  const safeLine = Math.max(1, Math.min(line, state.doc.lines))
  const documentLine = state.doc.line(safeLine)
  const safeColumn = Math.max(0, Math.min(column, documentLine.length))
  return documentLine.from + safeColumn
}

function createDiagnostic(state: EditorState, issue: ToolPylintIssue): Diagnostic {
  const from = getDocumentPosition(state, issue.line, issue.column)
  const endPosition = getDocumentPosition(state, issue.endLine ?? issue.line, issue.endColumn ?? issue.column + 1)

  return { from: Math.min(from, endPosition), message: issue.message, severity: issue.type, to: Math.max(from, endPosition) }
}

const codeLinter = linter(
  async (view) => {
    const lintSource = view.state.doc.toString()
    if (!lintSource.trim()) return []

    return ToolApi.postToolPylint(lintSource)
      .then((issues) => {
        if (lintSource !== view.state.doc.toString()) return []
        return issues.slice(0, 50).map((issue) => createDiagnostic(view.state, issue))
      })
      .catch(() => [])
  },
  { delay: 500 },
)

const extensions = [python(), codeLinter]

/* 全屏编辑 */
const dialogVisible = ref(false)
const dialogCode = ref('')

function openEditorDialog() {
  dialogCode.value = code.value
  dialogVisible.value = true
}

function closeEditorDialog() {
  dialogVisible.value = false
}

function submitEditorDialog() {
  code.value = dialogCode.value
  emit('submitDialog', dialogCode.value)
  closeEditorDialog()
}
</script>

<template>
  <div class="mk-codemirror w-full relative">
    <Codemirror v-model="code" :extensions="extensions" :tab-size="4" autofocus v-bind="$attrs" :style="{ height: '210px' }" />
    <el-button class="absolute right-2 bottom-2" text type="info" @click="openEditorDialog">
      <MkIcon name="icon_magnify_outlined" />
    </el-button>
  </div>

  <MkDialog v-model="dialogVisible" :title="title" append-to-body fullscreen>
    <template #header="{ titleClass, titleId }">
      <div class="flex-between pr-8">
        <span :id="titleId" :class="titleClass">{{ title }}</span>
        <slot name="header-extra" />
      </div>
    </template>

    <div class="mk-codemirror">
      <Codemirror v-model="dialogCode" autofocus :extensions="extensions" :tab-size="4" :style="{ height: 'calc(100dvh - 160px)' }" />
    </div>

    <template #footer>
      <el-button type="primary" @click="submitEditorDialog">确定</el-button>
    </template>
  </MkDialog>
</template>

<style lang="scss" scoped>
@use './style.scss';
</style>
