<script setup lang="ts">
import { computed, provide, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, KnowledgeWorkflowApi, KnowledgeWorkflowDebugPayload } from '@/api/types'
import type { FormField } from '@/components/mk-dynamics-form'
import type LogicFlow from '@logicflow/core'
import type { AxiosProgressEvent } from 'axios'
import type { Component } from 'vue'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import FileApi from '@/api/admin/file'
import DataSource from '@/views/workflow/knowledge/debug/action/DataSource.vue'
import KnowledgeBase from '@/views/workflow/knowledge/debug/action/KnowledgeBase.vue'
import Result from '@/views/workflow/knowledge/debug/action/Result.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'WorkflowImportDocumentDrawer' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ api: KnowledgeWorkflowApi; knowledgeId: string }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()

/* 复用工作流 Action，上传适配保留进度、取消和上传中保护。 */
const uploadingCount = ref(0)
provide('upload', (file: File, onProgress?: (percent: number, event: AxiosProgressEvent) => void) => {
  uploadingCount.value += 1
  const upload = FileApi.postUploadFile(
    file,
    undefined,
    FILE_SOURCE_TYPE.TEMPORARY_120_MINUTE,
    typeof onProgress === 'function' ? onProgress : undefined,
  )
  // 普通上传项等待 Promise，本地文件项还使用 abort；同时适配两种现有协议。
  return Object.assign(
    upload.request
      .then((url) => ({ data: url }))
      .finally(() => {
        uploadingCount.value -= 1
      }),
    { abort: upload.abort },
  )
})
provide('delFile', FileApi.deleteFile)

/* 数据源、知识库输入及执行结果与 DebugDrawer 保持一致。 */
type ActionStep = 'data_source' | 'knowledge_base' | 'result'
const actionComponents: Record<ActionStep, Component> = { data_source: DataSource, knowledge_base: KnowledgeBase, result: Result }
const visible = ref(false)
const currentWorkflow = ref<LogicFlow.GraphConfigData | null>(null)
const loading = ref(false)
const active = ref<ActionStep>('data_source')
const activeStep = computed(() => ({ data_source: 0, knowledge_base: 1, result: 2 })[active.value])
const actionKey = ref(0)
const actionId = ref<string>()
const formPayload = ref<KnowledgeWorkflowDebugPayload>({ data_source: {}, knowledge_base: {} })
const actionRef = useTemplateRef<{ validate: () => Promise<unknown>; getData: () => Dict<unknown> }>('actionRef')
const knowledgeBaseNode = computed(() => currentWorkflow.value?.nodes?.find((node) => node.type === WorkflowNodeType.KnowledgeBase))
const hasKnowledgeBaseInput = computed(
  () => ((knowledgeBaseNode.value?.properties?.user_input_field_list as FormField[] | undefined)?.length ?? 0) > 0,
)
const userInputTitle = computed(() => knowledgeBaseNode.value?.properties?.user_input_config?.title || t('workflow.userInput.title'))
const showNext = computed(() => hasKnowledgeBaseInput.value && active.value === 'data_source')
const showPrev = computed(() => hasKnowledgeBaseInput.value && active.value === 'knowledge_base')
const showImport = computed(() => (hasKnowledgeBaseInput.value ? active.value === 'knowledge_base' : active.value === 'data_source'))
function open(workflow?: LogicFlow.GraphConfigData) {
  currentWorkflow.value = workflow ?? null
  visible.value = true
}
function getActionData() {
  const data = actionRef.value?.getData() ?? {}
  const sourceNode = currentWorkflow.value?.nodes?.find((node) => node.id === data.node_id)
  // 本地上传校验 file_id；工具数据源的 file_list 保留远程文件选择协议。
  if (sourceNode?.type === WorkflowNodeType.DataSourceLocalNode && Array.isArray(data.file_list)) {
    const successfulFiles = data.file_list.filter((file) => file.file_id && (!file.status || file.status === 'success'))
    data.file_list = successfulFiles
    if (!successfulFiles.length) {
      MsgWarning(t('upload.noSuccessfulFilesMessage'))
      return undefined
    }
  }
  return data
}
function handleNext() {
  if (loading.value || uploadingCount.value > 0) return
  return actionRef.value
    ?.validate()
    .then(() => {
      const data = getActionData()
      if (!data) return
      formPayload.value.data_source = data
      active.value = 'knowledge_base'
    })
    .catch(() => {
      /* Action 展示校验错误。 */
    })
}
function handlePrevious() {
  if (loading.value || uploadingCount.value > 0) return
  formPayload.value.knowledge_base = actionRef.value?.getData() ?? {}
  active.value = 'data_source'
}
function handleSubmit() {
  if (loading.value || uploadingCount.value > 0 || active.value === 'result' || !actionRef.value) return
  const step = active.value
  loading.value = true
  return actionRef.value
    .validate()
    .then(() => {
      const data = getActionData()
      if (!data) return
      formPayload.value[step] = data
      return props.api.postKnowledgeWorkflowImport(props.knowledgeId, formPayload.value).then((action) => {
        actionId.value = action.id
        active.value = 'result'
        emit('refresh')
      })
    })
    .catch(() => {
      /* 请求层统一提示错误，保留表单供重试。 */
    })
    .finally(() => {
      loading.value = false
    })
}
function handleContinueImport() {
  if (loading.value || uploadingCount.value > 0) return
  formPayload.value = { data_source: {}, knowledge_base: {} }
  actionId.value = undefined
  actionKey.value += 1
  active.value = 'data_source'
}
function handleFinish() {
  visible.value = false
  emit('refresh')
}
defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" @closed="emit('closed')">
    <template #header>
      <div class="flex w-full">
        <h4>{{ t('knowledge.document.import.title') }}</h4>
        <el-steps v-if="hasKnowledgeBaseInput" :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step :title="t('resource.dataSource.selectTitle')" />
          <el-step :title="userInputTitle" />
        </el-steps>
      </div>
    </template>
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <keep-alive :key="actionKey" :include="['DataSource', 'KnowledgeBase']">
        <component
          :is="actionComponents[active]"
          :api="api"
          ref="actionRef"
          v-model:loading="loading"
          :workflow="currentWorkflow"
          :knowledge-id="knowledgeId"
          :action-id="actionId"
        />
      </keep-alive>
    </div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button v-if="active !== 'result'" plain :disabled="loading || uploadingCount > 0" @click="visible = false">
        {{ t('common.actions.cancel') }}
      </el-button>
      <!-- 继续导入 -->
      <el-button v-if="active === 'result'" plain @click="handleContinueImport">{{ t('knowledge.document.import.continue') }}</el-button>
      <!-- 返回数据源 -->
      <el-button v-if="showPrev" plain :disabled="loading || uploadingCount > 0" @click="handlePrevious">
        {{ t('common.actions.previous') }}
      </el-button>
      <!-- 进入用户输入 -->
      <el-button v-if="showNext" type="primary" :disabled="loading || uploadingCount > 0" @click="handleNext">
        {{ t('common.actions.next') }}
      </el-button>
      <!-- 执行工作流导入 -->
      <el-button v-if="showImport" type="primary" :loading="loading" :disabled="uploadingCount > 0" @click="handleSubmit">
        {{ t('knowledge.document.import.start') }}
      </el-button>
      <!-- 完成导入 -->
      <el-button v-if="active === 'result'" type="primary" @click="handleFinish">{{ t('knowledge.document.import.goToDocuments') }}</el-button>
    </template>
  </MkDrawer>
</template>
