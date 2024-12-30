<template>
  <Codemirror
    v-bind="$attrs"
    ref="cmRef"
    :extensions="extensions"
    :style="codemirrorStyle"
    :tab-size="4"
    :autofocus="true"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Codemirror } from 'vue-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { linter, type Diagnostic } from '@codemirror/lint'
import FunctionApi from '@/api/function-lib'

defineOptions({ name: 'CodemirrorEditor' })

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
  height: '210px!important'
}
const cmRef = ref<InstanceType<typeof Codemirror>>()
</script>

<style lang="scss"></style>
