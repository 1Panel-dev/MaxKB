<script setup lang="ts">
import { ref } from 'vue'
import JsonEditor from '@/components/codemirror-editor/Json.vue'
import type { DynamicFormValue } from '../type'

defineOptions({ name: 'DynamicFormJsonInput', inheritAttrs: false })

const modelValue = defineModel<DynamicFormValue>({
  default: () => ({}),
})

const jsonEditorRef = ref<InstanceType<typeof JsonEditor>>()

function validateRules(rule: unknown, value: DynamicFormValue, callback: (error?: Error) => void) {
  return jsonEditorRef.value?.validateRules(rule, value, callback)
}

defineExpose({ validateRules })
</script>

<template>
  <JsonEditor ref="jsonEditorRef" v-model="modelValue" v-bind="$attrs" />
</template>
