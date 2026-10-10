<script setup lang="ts">
import { computed, provide, ref, useTemplateRef, type Component } from 'vue'
import { useRouter } from 'vue-router'
import type { AxiosProgressEvent } from 'axios'
import type LogicFlow from '@logicflow/core'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { Dict, KnowledgeWorkflowDebugPayload } from '@/api/types'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { getWorkspaceId } from '@/utils/resource-context'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import type { FormField } from '@/components/mk-dynamics-form'
import DataSource from './action/DataSource.vue'
import KnowledgeBase from './action/KnowledgeBase.vue'
import Result from './action/Result.vue'

defineOptions({ name: 'KnowledgeWorkflowDebugDrawer' })

const props = defineProps<{ knowledgeId: string }>()
const router = useRouter()

type ActionStep = 'data_source' | 'knowledge_base' | 'result'

const actionComponents: Record<ActionStep, Component> = { data_source: DataSource, knowledge_base: KnowledgeBase, result: Result }

// mk-dynamics-form 的上传项通过 inject('upload') 获取上传函数；返回值的 data 为文件地址（末段即 file_id）。
provide('upload', (file: File, onProgress?: (percent: number, event: AxiosProgressEvent) => void) => {
  const upload = FileApi.postUploadFile(
    file,
    props.knowledgeId,
    FILE_SOURCE_TYPE.KNOWLEDGE,
    typeof onProgress === 'function' ? onProgress : undefined,
  )
  return Object.assign(
    upload.request.then((url) => ({ data: url })),
    { abort: upload.abort },
  )
})

// 调试步骤与表单缓存。
const visible = ref(false)
const loading = ref(false)
const active = ref<ActionStep>('data_source')
const actionKey = ref(0)
const actionId = ref<string>()
const currentWorkflow = ref<LogicFlow.GraphConfigData | null>(null)
const formPayload = ref<KnowledgeWorkflowDebugPayload>({ data_source: {}, knowledge_base: {} })

const actionRef = useTemplateRef<{ validate: () => Promise<unknown>; getData: () => Dict<unknown> }>('actionRef')

// 知识库节点存在用户输入字段时，才需要「数据源 → 知识库输入」两步。
const knowledgeBaseNode = computed(() => currentWorkflow.value?.nodes?.find((node) => node.type === WorkflowNodeType.KnowledgeBase))
const hasKnowledgeBaseInput = computed(
  () => ((knowledgeBaseNode.value?.properties?.user_input_field_list as FormField[] | undefined)?.length ?? 0) > 0,
)
const userInputTitle = computed(() => knowledgeBaseNode.value?.properties?.user_input_config?.title || '用户输入')
const activeStep = computed(() => ({ data_source: 0, knowledge_base: 1, result: 2 })[active.value])

const showNext = computed(() => hasKnowledgeBaseInput.value && active.value === 'data_source')
const showPrev = computed(() => hasKnowledgeBaseInput.value && active.value === 'knowledge_base')
const showImport = computed(() => (hasKnowledgeBaseInput.value ? active.value === 'knowledge_base' : active.value === 'data_source'))

function next() {
  if (loading.value || !showNext.value) return
  return actionRef.value
    ?.validate()
    .then(() => {
      formPayload.value.data_source = actionRef.value?.getData() ?? {}
      active.value = 'knowledge_base'
    })
    .catch(() => {
      // 表单展示校验错误，保留当前步骤。
    })
}

function prev() {
  if (loading.value || !showPrev.value) return
  formPayload.value.knowledge_base = actionRef.value?.getData() ?? {}
  active.value = 'data_source'
}

function submit() {
  if (loading.value || active.value === 'result' || !actionRef.value) return
  const step = active.value
  loading.value = true
  return actionRef.value
    .validate()
    .then(() => {
      formPayload.value[step] = actionRef.value?.getData() ?? {}
      return KnowledgeWorkflowApi.postKnowledgeWorkflowDebug(props.knowledgeId, formPayload.value).then((action) => {
        actionId.value = action.id
        active.value = 'result'
      })
    })
    .catch(() => {
      // 校验和请求错误由各自流程提示，保留表单供重试。
    })
    .finally(() => {
      loading.value = false
    })
}

// 继续导入：重置表单并强制重建动作组件，保留当前工作流。
function continueImporting() {
  if (loading.value) return
  actionId.value = undefined
  formPayload.value = { data_source: {}, knowledge_base: {} }
  active.value = 'data_source'
  actionKey.value += 1
}

// 抽屉生命周期与文档导航。
function open(workflow: LogicFlow.GraphConfigData) {
  currentWorkflow.value = workflow
  visible.value = true
}

function close() {
  visible.value = false
}

function handleClosed() {
  currentWorkflow.value = null
  active.value = 'data_source'
  actionId.value = undefined
  formPayload.value = { data_source: {}, knowledge_base: {} }
}

function handleGoToDocuments() {
  return router
    .push({
      name: 'workspace-knowledge-document-list',
      params: { workspaceId: getWorkspaceId(), knowledgeId: props.knowledgeId, type: KNOWLEDGE_TYPE_KEY.WORKFLOW },
    })
    .then(close)
}

defineExpose({ open, close })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" @closed="handleClosed">
    <template #header>
      <div class="flex w-full">
        <h4>调试</h4>
        <el-steps v-if="hasKnowledgeBaseInput" :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step title="选择数据源" />
          <el-step :title="userInputTitle" />
        </el-steps>
      </div>
    </template>
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <keep-alive :key="actionKey" :include="['DataSource', 'KnowledgeBase']">
        <component
          :is="actionComponents[active]"
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
      <el-button plain v-if="active !== 'result'" :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 继续导入 -->
      <el-button v-if="active === 'result'" plain @click="continueImporting">继续导入</el-button>
      <!-- 返回数据源 -->
      <el-button v-if="showPrev" plain :disabled="loading" @click="prev">上一步</el-button>
      <!-- 进入用户输入 -->
      <el-button v-if="showNext" type="primary" :disabled="loading" @click="next">下一步</el-button>
      <!-- 开始导入 -->
      <el-button v-if="showImport" type="primary" :loading="loading" @click="submit">开始导入</el-button>
      <!-- 前往工作流知识库文档 -->
      <el-button v-if="active === 'result'" type="primary" @click="handleGoToDocuments">前往文档</el-button>
    </template>
  </MkDrawer>
</template>
