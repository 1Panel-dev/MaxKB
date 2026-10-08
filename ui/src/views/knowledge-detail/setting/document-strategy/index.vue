<script setup lang="ts">
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { ref, useTemplateRef, watch } from 'vue'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import DocumentStrategyForm from '@/views/knowledge/create-knowledge/components/DocumentStrategyForm.vue'
import { MsgSuccess } from '@/utils/message'
import { useKnowledgeDetailContext } from '../../context'

defineOptions({ name: 'KnowledgeDocumentStrategyView' })

defineProps<ResourceDetailPageProps>()

/* 复用详情回填策略，草稿由表单维护。 */
const { knowledge, replaceKnowledgeDetail } = useKnowledgeDetailContext()
const strategyFormRef = useTemplateRef<InstanceType<typeof DocumentStrategyForm>>('strategyFormRef')
const saving = ref(false)
watch(
  [knowledge, strategyFormRef],
  ([detail, strategyForm]) => {
    if (detail && strategyForm) strategyForm.setStrategy(detail.doc_strategy)
  },
  { immediate: true, flush: 'post' },
)

/* 只保存文档处理策略，不触发同步或修改其他设置。 */
function handleSave() {
  const detail = knowledge.value
  const strategyForm = strategyFormRef.value
  if (saving.value || !detail || !strategyForm) return
  saving.value = true
  return strategyForm
    .validate()
    .then((valid) => {
      if (!valid) return
      return KnowledgeApi.putKnowledge(detail.id, { doc_strategy: strategyForm.getStrategy() }).then((savedKnowledge) => {
        replaceKnowledgeDetail({ ...detail, ...savedKnowledge })
        MsgSuccess('保存成功')
      })
    })
    .catch(() => {})
    .finally(() => {
      saving.value = false
    })
}

defineExpose({ customHeader: true })
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-align-center flex-wrap gap-2">
      <h4>{{ title }}</h4>
      <span class="text-N600">同步知识库时若有新的 URL 按该策略执行，策略变更后下次同步知识库时生效</span>
    </div>
  </Teleport>
  <div v-loading="saving" class="max-w-200">
    <DocumentStrategyForm ref="strategyFormRef" />
    <!-- 保存文档处理策略 -->
    <el-button type="primary" class="mt-4" :loading="saving" @click="handleSave">保存</el-button>
  </div>
</template>
