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
import { Codemirror } from 'vue-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { linter, type Diagnostic } from '@codemirror/lint'
import FunctionApi from '@/api/function-lib'

defineOptions({ name: 'CodemirrorEditor' })

const props = defineProps<{
  title: String
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue', 'submitDialog'])
const data = computed({
  set: (value) => {
    emit('update:modelValue', value)
  },
  get: () => {
    return props.modelValue
  }
})

function getRangeFromLineAndColumn(state: any, line: number, column: number, end_column?: number) {
  const l = state.doc.line(line)
  const form = l.from + column
  const to_end_column = l.from + end_column
  return {
    form: form > l.to ? l.to : form,
    to: end_column && to_end_column < l.to ? to_end_column : l.to
  }
}

const regexpLinter = linter(async (view) => {
  let diagnostics: Diagnostic[] = []
  await FunctionApi.pylint(view.state.doc.toString()).then((ok) => {
    ok.data.forEach((element: any) => {
      const range = getRangeFromLineAndColumn(
        view.state,
        element.line,
        element.column,
        element.endColumn
      )

      diagnostics.push({
        from: range.form,
        to: range.to,
        severity: element.type,
        message: element.message
      })
    })
  })
  return diagnostics
})
const extensions = [python(), regexpLinter, oneDark]
const codemirrorStyle = {
  height: '210px!important',
  width: '100%'
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
