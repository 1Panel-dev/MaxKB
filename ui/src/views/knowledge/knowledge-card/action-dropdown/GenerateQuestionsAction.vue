<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { DocumentTaskState, KnowledgeItem, RelatedQuestionsConfig } from '@/api/types'
import GenerateQuestionsDialog from '@/components/business/generate-questions/GenerateQuestionsDialog.vue'
import { MsgSuccess } from '@/utils/message'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'

defineOptions({ name: 'GenerateQuestionsAction' })
const props = defineProps<{ api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi; knowledge: KnowledgeItem; label: string }>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库生成问题配置：按需挂载并固定本次操作目标。 */
const dialogMounted = ref(false)
const dialogRef = useTemplateRef<InstanceType<typeof GenerateQuestionsDialog>>('dialogRef')
const targetKnowledgeId = ref('')

function handleOpenDialog() {
  if (loading.value || dialogMounted.value) return
  targetKnowledgeId.value = props.knowledge.id
  dialogMounted.value = true
  return nextTick(() => dialogRef.value?.open())
}

/* 知识库 Action 独立提交知识库接口。 */
function handleSubmit(config: RelatedQuestionsConfig, stateList: DocumentTaskState[]) {
  if (loading.value) return
  loading.value = true
  return props.api
    .putGenerateKnowledgeQuestions(targetKnowledgeId.value, { ...config, state_list: stateList })
    .then(() => {
      MsgSuccess('任务已提交')
      dialogRef.value?.close()
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  dialogMounted.value = false
  targetKnowledgeId.value = ''
}
</script>

<template>
  <!-- 生成知识库关联问题 -->
  <MkDropdownItem :disabled="loading" @click.stop="handleOpenDialog">
    <template #icon><MkIcon name="icon_link-record_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <GenerateQuestionsDialog v-if="dialogMounted" ref="dialogRef" :loading="loading" @submit="handleSubmit" @closed="handleClosed" />
</template>
