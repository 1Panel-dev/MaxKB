<script setup lang="ts">
import { computed, ref } from 'vue'
import { MkDynamicsForm, type DynamicFormValue, type FormField } from '@/components/mk-dynamics-form'
import type { Dict } from '@/api/types'
import { WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'KnowledgeBase' })

interface WorkflowNode {
  id: string
  type: WorkflowNodeType
  properties: {
    user_input_config?: { title?: string }
    user_input_field_list?: FormField[]
  } & Dict<unknown>
}

const props = defineProps<{ workflow: { nodes?: WorkflowNode[] } | null }>()

const dynamicsFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const formData = ref<Dict<DynamicFormValue>>({})

const knowledgeBaseNode = computed(() => props.workflow?.nodes?.find((node) => node.type === WorkflowNodeType.KnowledgeBase))
const chatTitle = computed(() => knowledgeBaseNode.value?.properties.user_input_config?.title || '用户输入')
const baseFormList = computed<FormField[]>(() => knowledgeBaseNode.value?.properties.user_input_field_list ?? [])

function validate() {
  return dynamicsFormRef.value?.validate() ?? Promise.resolve()
}

function getData() {
  return formData.value
}

defineExpose({ validate, getData })
</script>

<template>
  <MkDynamicsForm ref="dynamicsFormRef" v-model="formData" :render-data="baseFormList" label-position="top" require-asterisk-position="right">
    <template #default>
      <h4 class="mb-4 mt-1">{{ chatTitle }}</h4>
    </template>
  </MkDynamicsForm>
</template>
