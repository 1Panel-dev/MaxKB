<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DocumentResourceType, KnowledgeItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { DOCUMENT_RESOURCE_TYPE, KNOWLEDGE_TYPE } from '@/api/enums'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DocumentMigrateDialog' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
  knowledgeId: string
  resourceType?: DocumentResourceType
}>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
const { resourceApi } = useKnowledgeDetailContext()
const visible = ref(false)
const loading = defineModel<boolean>('loading', { default: false })
const optionLoading = ref(false)
const knowledgeOptions = ref<KnowledgeItem[]>([])
const knowledgeById = computed(() => new Map(knowledgeOptions.value.map((knowledge) => [knowledge.id, knowledge])))
const migrateFormRef = useTemplateRef<FormInstance>('migrateFormRef')
const migrateForm = reactive({ targetKnowledgeId: '' })
const migrateRules = computed<FormRules<typeof migrateForm>>(() => ({
  targetKnowledgeId: [{ required: true, message: t('knowledge.fields.targetKnowledge.requiredMessage'), trigger: 'change' }],
}))
const targetDocumentIds = ref<string[]>([])

// 打开迁移弹窗，固定本次文档并查询目标知识库。
function open(documentIds: string[]) {
  if (loading.value || optionLoading.value || !documentIds.length) return
  targetDocumentIds.value = [...documentIds]
  visible.value = true
  optionLoading.value = true
  resourceApi.knowledge
    .getAllKnowledge({ knowledge_id: props.knowledgeId })
    .then((knowledge) => {
      knowledgeOptions.value = knowledge.filter(
        ({ id, type }) =>
          id !== props.knowledgeId &&
          (props.resourceType !== DOCUMENT_RESOURCE_TYPE.IMAGE || type === KNOWLEDGE_TYPE.BASE || type === KNOWLEDGE_TYPE.WORKFLOW),
      )
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      optionLoading.value = false
    })
}

// 迁移成功后关闭并通知页面刷新，失败保留选择。
async function handleSubmit() {
  if (loading.value || optionLoading.value || !(await migrateFormRef.value?.validate().catch(() => false))) return
  loading.value = true
  return (
    props.api
      .putMigrateDocuments?.(props.knowledgeId, migrateForm.targetKnowledgeId, targetDocumentIds.value)
      .then(() => {
        MsgSuccess(t('knowledge.messages.migrateSuccess'))
        visible.value = false
        emit('refresh')
      })
      .catch(() => {
        // 请求层统一提示错误，保留当前输入。
      }) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('knowledge.actions.migrateTo')" @closed="emit('closed')">
    <el-form
      ref="migrateFormRef"
      :model="migrateForm"
      :rules="migrateRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('knowledge.fields.targetKnowledge.label')" prop="targetKnowledgeId">
        <el-select
          v-model="migrateForm.targetKnowledgeId"
          fit-input-width
          filterable
          :placeholder="t('knowledge.fields.targetKnowledge.placeholder')"
          :loading="optionLoading"
        >
          <template v-for="target in knowledgeOptions" :key="target.id">
            <el-option :label="target.name" :value="target.id">
              <div class="flex-align-center min-w-0 gap-2">
                <KnowledgeIcon :type="target.type" :size="20" class="shrink-0" />
                <span class="truncate" :title="target.name">{{ target.name }}</span>
              </div>
            </el-option>
          </template>
          <template #label="{ label, value }">
            <span class="flex-align-center gap-2">
              <KnowledgeIcon :type="knowledgeById.get(value)?.type" :size="20" class="shrink-0" />
              <span class="truncate" :title="label">{{ label }}</span>
            </span>
          </template>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消文档迁移 -->
      <el-button plain :disabled="loading || optionLoading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确认迁移文档 -->
      <el-button type="primary" :loading="loading" :disabled="optionLoading" @click="handleSubmit">{{ t('common.actions.confirm') }}</el-button>
    </template>
  </MkDialog>
</template>
