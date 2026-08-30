<script setup lang="ts">
import { ref, watch } from 'vue'
import { DocumentChecked } from '@element-plus/icons-vue'
import { json, jsonParseLinter } from '@codemirror/lang-json'
import { linter } from '@codemirror/lint'
import { Codemirror } from 'vue-codemirror'

defineOptions({ name: 'JsonInput', inheritAttrs: false })

const modelValue = defineModel<unknown>({ required: true })
const props = withDefaults(defineProps<{ title?: string }>(), { title: 'JSON' })

const emit = defineEmits<{ submitDialog: [value: unknown] }>()

const extensions = [json(), linter(jsonParseLinter())]

function stringifyJson(value: unknown) {
  if (value === undefined || value === '') return ''
  return JSON.stringify(value, null, 4) ?? ''
}

function parseJson(content: string) {
  return JSON.parse(content || '{}') as unknown
}

const editorContent = ref(stringifyJson(modelValue.value))
let lastEmittedValue: unknown

watch(modelValue, (value) => {
  if (Object.is(value, lastEmittedValue)) {
    lastEmittedValue = undefined
    return
  }
  editorContent.value = stringifyJson(value)
})

function handleContentChange(content: string) {
  editorContent.value = content

  try {
    const value = parseJson(content)
    lastEmittedValue = value
    modelValue.value = value
  } catch {
    // 保留无法解析的编辑内容，交由 CodeMirror 和表单校验提示。
  }
}

function format() {
  try {
    handleContentChange(JSON.stringify(parseJson(editorContent.value), null, 4))
  } catch {
    // JSON 诊断会标记具体的语法错误位置。
  }
}

/* 全屏编辑 */
const dialogVisible = ref(false)
const dialogContent = ref('')

function openEditorDialog() {
  dialogContent.value = editorContent.value
  dialogVisible.value = true
}

function closeEditorDialog() {
  dialogVisible.value = false
}

function submitEditorDialog() {
  try {
    const value = parseJson(dialogContent.value)
    handleContentChange(dialogContent.value)
    emit('submitDialog', value)
    closeEditorDialog()
  } catch {
    // JSON 不合法时保留弹窗和编辑内容，等待用户修正。
  }
}

function validateRules(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  try {
    parseJson(editorContent.value)
    callback()
  } catch {
    callback(new Error('请输入正确的 JSON 格式'))
  }
}

defineExpose({ format, validateRules })
</script>

<template>
  <div class="relative w-full">
    <Codemirror
      :model-value="editorContent"
      :extensions="extensions"
      :tab-size="4"
      autofocus
      style="height: 210px; width: 100%"
      v-bind="$attrs"
      @update:model-value="handleContentChange"
    />
    <el-button class="absolute right-2 top-2" text type="info" @click="format">
      <MkIcon :icon="DocumentChecked" />
    </el-button>
    <el-button class="absolute bottom-2 right-2" text type="info" @click="openEditorDialog">
      <MkIcon name="icon_magnify_outlined" />
    </el-button>
  </div>

  <MkDialog v-model="dialogVisible" :title="props.title" append-to-body fullscreen>
    <Codemirror v-model="dialogContent" :extensions="extensions" :tab-size="4" autofocus style="height: calc(100vh - 160px)" />

    <template #footer>
      <el-button @click="closeEditorDialog">取消</el-button>
      <el-button type="primary" @click="submitEditorDialog">确定</el-button>
    </template>
  </MkDialog>
</template>
