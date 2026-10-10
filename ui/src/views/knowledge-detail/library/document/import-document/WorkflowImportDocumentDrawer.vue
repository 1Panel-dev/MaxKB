<script setup lang="ts">
import { computed, provide, ref, useTemplateRef, type Component } from 'vue'
import type { AxiosProgressEvent } from 'axios'
import type LogicFlow from '@logicflow/core'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { Dict, KnowledgeWorkflowDebugPayload } from '@/api/types'
import type { FormField } from '@/components/mk-dynamics-form'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import DataSource from '@/views/workflow/knowledge/debug/action/DataSource.vue'
import KnowledgeBase from '@/views/workflow/knowledge/debug/action/KnowledgeBase.vue'
import Result from '@/views/workflow/knowledge/debug/action/Result.vue'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'WorkflowImportDocumentDrawer' })
const props = defineProps<{ knowledgeId: string; workflow?: LogicFlow.GraphConfigData }>()
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
const loading = ref(false)
const active = ref<ActionStep>('data_source')
const actionKey = ref(0)
const actionId = ref<string>()
const formPayload = ref<KnowledgeWorkflowDebugPayload>({ data_source: {}, knowledge_base: {} })
const actionRef = useTemplateRef<{ validate: () => Promise<unknown>; getData: () => Dict<unknown> }>('actionRef')
const hasKnowledgeBaseInput = computed(() => {
  const node = props.workflow?.nodes?.find((node) => node.type === WorkflowNodeType.KnowledgeBase)
  return ((node?.properties?.user_input_field_list as FormField[] | undefined)?.length ?? 0) > 0
})
const busy = computed(() => loading.value || uploadingCount.value > 0)
function open() {
  visible.value = true
}
function getActionData() {
  const data = actionRef.value?.getData() ?? {}
  if (Array.isArray(data.file_list)) {
    const successfulFiles = data.file_list.filter((file) => file.file_id && (!file.status || file.status === 'success'))
    data.file_list = successfulFiles
    if (!successfulFiles.length) {
      MsgWarning('没有上传成功的文件，请重新上传')
      return undefined
    }
  }
  return data
}
function handleNext() {
  if (busy.value) return
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
  if (busy.value) return
  formPayload.value.knowledge_base = actionRef.value?.getData() ?? {}
  active.value = 'data_source'
}
function handleSubmit() {
  if (busy.value || active.value === 'result' || !actionRef.value) return
  const step = active.value
  loading.value = true
  return actionRef.value
    .validate()
    .then(() => {
      const data = getActionData()
      if (!data) return
      formPayload.value[step] = data
      return KnowledgeWorkflowApi.postKnowledgeWorkflowImport(props.knowledgeId, formPayload.value).then((action) => {
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
  if (busy.value) return
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
    <!-- <template #header>
      <div class="flex w-full">
        <h4>导入文档</h4>
        <el-steps :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step title="导入文档" />
          <el-step title="文档处理策略" />
        </el-steps>
      </div>
    </template> -->
    <div v-loading="loading" class="h-full">
      <keep-alive :key="actionKey" :include="['DataSource', 'KnowledgeBase']">
        <component
          :is="actionComponents[active]"
          ref="actionRef"
          v-model:loading="loading"
          :workflow="workflow ?? null"
          :knowledge-id="knowledgeId"
          :action-id="actionId"
        />
      </keep-alive>
    </div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button v-if="active !== 'result'" :disabled="busy" @click="visible = false">取消</el-button>
      <!-- 继续导入 -->
      <el-button v-if="active === 'result'" @click="handleContinueImport">继续导入</el-button>
      <!-- 返回数据源 -->
      <el-button v-if="hasKnowledgeBaseInput && active === 'knowledge_base'" :disabled="busy" @click="handlePrevious">上一步</el-button>
      <!-- 进入知识库输入 -->
      <el-button v-if="hasKnowledgeBaseInput && active === 'data_source'" :disabled="busy" @click="handleNext">下一步</el-button>
      <!-- 执行工作流导入 -->
      <el-button
        v-if="hasKnowledgeBaseInput ? active === 'knowledge_base' : active === 'data_source'"
        type="primary"
        :loading="loading"
        :disabled="uploadingCount > 0"
        @click="handleSubmit"
      >
        导入
      </el-button>
      <!-- 完成导入 -->
      <el-button v-if="active === 'result'" type="primary" @click="handleFinish">完成</el-button>
    </template>
  </MkDrawer>
</template>
