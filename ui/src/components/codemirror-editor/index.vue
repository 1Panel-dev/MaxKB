<template>
  <div class="codemirror-editor w-full">
    <Codemirror
      v-model="data"
      ref="cmRef"
      :extensions="extensions"
      :style="codemirrorStyle"
      :tab-size="4"
      :autofocus="true"
      v-bind="$attrs"
    />

    <div class="codemirror-editor__footer">
      <el-button text type="info" @click="openCodemirrorDialog" class="magnify">
        <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
      </el-button>
    </div>
    <!-- Codemirror 弹出层 -->
    <el-dialog v-model="dialogVisible" :title="title" append-to-body fullscreen>
      <Codemirror
        v-model="cloneContent"
        :extensions="extensions"
        :style="codemirrorStyle"
        :tab-size="4"
        :autofocus="true"
        style="
          height: calc(100vh - 160px) !important;
          border: 1px solid #bbbfc4;
          border-radius: 4px;
        "
      />
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> {{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Codemirror } from 'vue-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { linter, type Diagnostic } from '@codemirror/lint'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { throttle } from 'lodash'

defineOptions({ name: 'CodemirrorEditor' })

const props = defineProps<{
  title: string
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue', 'submitDialog'])

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const data = computed({
  set: (value) => {
    emit('update:modelValue', value)
  },
  get: () => {
    return props.modelValue
  },
})

function getRangeFromLineAndColumn(state: any, line: number, column: number, end_column?: number) {
  const l = state.doc.line(line)
  const lineLength = l.length
  const safeColumn = Math.max(0, Math.min(column, lineLength))
  const fromPos = l.from + safeColumn
  let safeEndColumn
  if (end_column !== undefined) {
    safeEndColumn = Math.max(0, Math.min(end_column, lineLength))
  } else {
    safeEndColumn = lineLength
  }
  const toPos = l.from + safeEndColumn
  const finalFrom = Math.min(fromPos, toPos)
  const finalTo = Math.max(fromPos, toPos)
  return {
    from: finalFrom,
    to: finalTo,
  }
}
const asyncLint = throttle(async (view: any) => {
  const res = await loadSharedApi({ type: 'tool', systemType: apiType.value }).postPylint(
    view.state.doc.toString(),
  )
  return res.data
}, 500)

const regexpLinter = linter(async (view) => {
  const currentstate = view.state
  const diagnostics: Diagnostic[] = []
  const lintResults = await asyncLint(view)
  if (!lintResults || lintResults.length === 0) {
    return diagnostics
  }
  // 限制诊断数量，避免过多诊断信息
  const maxDiagnostics = 50
  const limitedResults = lintResults.slice(0, maxDiagnostics)

  limitedResults.forEach((element: any) => {
    try {
      const range = getRangeFromLineAndColumn(
        currentstate,
        element.line,
        element.column,
        element.endColumn,
      )
      // 验证范围有效性
      if (range.from >= 0 && range.to >= range.from) {
        diagnostics.push({
          from: range.from,
          to: range.to,
          severity: element.type === 'error' ? 'error' : 'warning',
          message: element.message,
        })
      }
    } catch (error) {
      // console.error('Error processing lint result:', error)
    }
  })
  return diagnostics
})
const extensions = [python(), oneDark, regexpLinter]
const codemirrorStyle = {
  height: '210px!important',
  width: '100%',
}
const cmRef = ref<InstanceType<typeof Codemirror>>()
// 弹出框相关代码
const dialogVisible = ref<boolean>(false)

const cloneContent = ref<string>('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    emit('submitDialog', cloneContent.value)
  }
})

const openCodemirrorDialog = () => {
  cloneContent.value = props.modelValue
  dialogVisible.value = true
}

function submitDialog() {
  emit('submitDialog', cloneContent.value)
  dialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.codemirror-editor {
  position: relative;

  &__footer {
    position: absolute;
    bottom: 10px;
    right: 10px;
  }
}
</style>
