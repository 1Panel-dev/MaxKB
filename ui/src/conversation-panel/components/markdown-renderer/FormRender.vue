<script setup lang="ts">
import { computed } from 'vue'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'
import type { DynamicFormValue, FormField } from '@/components/mk-dynamics-form'
import type { Dict } from '@/api/types'

defineOptions({ name: 'MarkdownFormRender' })

const props = defineProps<{ formSetting: string }>()

interface FormSetting {
  form_field_list?: FormField[]
  form_data?: Dict<DynamicFormValue>
  is_submit?: boolean
}

// v2 表单的提交依赖 runtime_node_id / child_node，与 v3 续跑协议不兼容，这里只读展示
const formSetting = computed<FormSetting>(() => {
  try {
    return JSON.parse(props.formSetting || '{}')
  } catch {
    return {}
  }
})
</script>

<template>
  <div>
    <MkDynamicsForm view :render-data="formSetting.form_field_list ?? []" :model-value="formSetting.form_data ?? {}" />
    <div v-if="!formSetting.is_submit" class="text-N500">旧版表单暂不支持提交</div>
  </div>
</template>
