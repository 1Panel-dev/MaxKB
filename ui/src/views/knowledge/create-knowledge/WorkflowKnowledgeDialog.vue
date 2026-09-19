<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import type { KnowledgeWorkflowTemplate, WorkflowStoreTemplate } from '@/api/types'
import { knowledgeTemplate } from '../template.ts'
import WorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import KnowledgeBaseForm from './components/KnowledgeBaseForm.vue'

defineOptions({ name: 'CreateWorkflowKnowledgeDialog' })
const props = defineProps<{ folderId: string }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
const { auth } = useStore()
const route = useRoute()
const router = useRouter()

/* 创建表单 */
const baseFormRef = useTemplateRef<InstanceType<typeof KnowledgeBaseForm>>('baseFormRef')
const dialogVisible = ref(false)
const loading = ref(false)
const workflowTemplate = ref<KnowledgeWorkflowTemplate>()

function resetData() {
  baseFormRef.value?.reset()
  workflowTemplate.value = undefined
  loading.value = false
}

function open(template?: KnowledgeWorkflowTemplate & Partial<Pick<WorkflowStoreTemplate, 'name' | 'desc' | 'description'>>) {
  resetData()
  workflowTemplate.value = template ? cloneDeep(template) : undefined
  dialogVisible.value = true
  nextTick(() => {
    if (template && baseFormRef.value) {
      Object.assign(baseFormRef.value.form, { name: template.name ?? '', desc: template.description ?? template.desc ?? '' })
    }
  })
}

function handleBeforeClose(done: () => void) {
  if (!loading.value) done()
}

function handleClosed() {
  resetData()
  emit('closed')
}

/* 校验并创建，成功后刷新资料并进入画布 */
function submit() {
  if (loading.value) return
  loading.value = true
  return Promise.all([baseFormRef.value?.validate()])
    .then((validationResults) => {
      if (!validationResults.every(Boolean) || !baseFormRef.value) return
      const baseForm = baseFormRef.value.form
      return WorkflowApi.postKnowledgeWorkflow({
        name: baseForm.name.trim(),
        desc: baseForm.desc.trim(),
        embedding_model_id: baseForm.embedding_model_id,
        folder_id: props.folderId,
        type: KNOWLEDGE_TYPE.WORKFLOW,
        work_flow: cloneDeep(knowledgeTemplate.default),
        work_flow_template: workflowTemplate.value ? cloneDeep(workflowTemplate.value) : undefined,
      }).then((knowledge) => {
        return auth.loadAuthBaseProfile().then(() => {
          MsgSuccess('创建成功')
          dialogVisible.value = false
          emit('refresh')
          return router.push({
            name: 'workflow-knowledge',
            params: { knowledgeId: knowledge.id, workspaceId: route.params.workspaceId },
          })
        })
      })
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="创建工作流知识库" align-center :before-close="handleBeforeClose" @closed="handleClosed">
    <KnowledgeBaseForm ref="baseFormRef" :disabled="loading" />
    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="dialogVisible = false">取消</el-button>
      <!-- 创建知识库 -->
      <el-button type="primary" :loading="loading" @click="submit">创建</el-button>
    </template>
  </MkDialog>
</template>
