<script setup lang="ts">
import { nextTick, onMounted, provide, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { cloneDeep } from 'lodash'
import ModelApi from '@/api/admin/workspace/model/model'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import type { DefaultModelSettingPayload, KnowledgeDetail, KnowledgeWorkflowDetail } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultKnowledgeNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode } from '@/workflow-canvas/types'
import WorkflowViewLayout from '../components/WorkflowViewLayout.vue'
import DefaultModelSettingButton from '../components/default-model-setting/DefaultModelSettingButton.vue'
import DebugDrawer from './debug/DebugDrawer.vue'

defineOptions({ name: 'KnowledgeWorkflowView' })

// 为画布节点中的 SelectModel 提供参数表单接口。
provide('getModelParamsForm', ModelApi.getModelParamsForm)

const DEFAULT_WORKFLOW: LogicFlow.GraphConfigData = {
  nodes: cloneDeep(defaultKnowledgeNodes),
  edges: [],
}

const route = useRoute()
const router = useRouter()
const knowledgeId = route.params.knowledgeId as string
const workspaceId = route.params.workspaceId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

/* 默认模型设置：抽屉提交后保存，失败时恢复上次已保存的配置。 */
const defaultModelSetting = ref<DefaultModelSettingPayload>({})
const savedDefaultModelSetting = ref<DefaultModelSettingPayload>({})

function handleApplyDefaultModelToAll(graphData: LogicFlow.GraphData) {
  workflowRef.value?.renderGraphData(graphData)
}

function handleSaveDefaultModelSetting(settings: DefaultModelSettingPayload) {
  defaultModelSetting.value = cloneDeep(settings)
  return handleSave()
}

/* 知识库工作流加载与保存 */
const knowledgeDetail = ref<KnowledgeDetail>()
const loading = ref(false)
const saving = ref(false)
const publishing = ref(false)
const savedWorkflow = ref<LogicFlow.GraphData>()
const saveTime = ref<Date | string>()

function getGraphData() {
  return workflowRef.value?.getGraphData()
}

function setSavedWorkflow(graphData: LogicFlow.GraphData) {
  savedWorkflow.value = cloneDeep(graphData)
}

function hasUnsavedChanges() {
  const graphData = getGraphData()
  if (!graphData || !savedWorkflow.value) return false

  return JSON.stringify(graphData) !== JSON.stringify(savedWorkflow.value)
}

function saveKnowledgeWorkflow(graphData = getGraphData(), showMessage = false) {
  if (!graphData) return Promise.resolve<KnowledgeWorkflowDetail | undefined>(undefined)

  saving.value = true
  return KnowledgeWorkflowApi.putKnowledgeWorkflow(knowledgeId, { work_flow: graphData, default_model_setting: cloneDeep(defaultModelSetting.value) })
    .then((knowledgeWorkflow) => {
      defaultModelSetting.value = cloneDeep(knowledgeWorkflow.default_model_setting ?? {})
      savedDefaultModelSetting.value = cloneDeep(defaultModelSetting.value)
      saveTime.value = knowledgeWorkflow.update_time || new Date()
      setSavedWorkflow(graphData)
      if (showMessage) MsgSuccess('保存成功')
      return knowledgeWorkflow
    })
    .catch((error) => {
      defaultModelSetting.value = cloneDeep(savedDefaultModelSetting.value)
      throw error
    })
    .finally(() => {
      saving.value = false
    })
}

function handleSave() {
  return saveKnowledgeWorkflow(undefined, true).catch(() => {})
}

/* 调试：先落库未保存的画布改动，保证调试命中最新工作流 */
const debugDrawerRef = useTemplateRef<InstanceType<typeof DebugDrawer>>('debugDrawerRef')

function openDebug() {
  const graphData = getGraphData()
  if (graphData) debugDrawerRef.value?.open(graphData)
}

function handleDebug() {
  if (hasUnsavedChanges()) {
    saveKnowledgeWorkflow(undefined, false)
      .then(() => openDebug())
      .catch(() => {})
    return
  }
  openDebug()
}

function handlePublish() {
  if (!workflowRef.value) return

  publishing.value = true
  workflowRef.value
    .validate()
    .then(() => saveKnowledgeWorkflow()) // 先保存未落库的画布改动
    .then(() => KnowledgeWorkflowApi.putKnowledgeWorkflowPublish(knowledgeId))
    .then(() => MsgSuccess('发布成功'))
    .catch(() => {})
    .finally(() => {
      publishing.value = false
    })
}

function loadKnowledgeWorkflow() {
  loading.value = true
  return KnowledgeApi.getKnowledgeDetail(knowledgeId)
    .then((knowledge) => {
      knowledgeDetail.value = knowledge
      defaultModelSetting.value = cloneDeep(knowledge.default_model_setting ?? {})
      savedDefaultModelSetting.value = cloneDeep(defaultModelSetting.value)
      saveTime.value = knowledge.update_time

      const workflow = knowledge.work_flow?.nodes?.length ? knowledge.work_flow : DEFAULT_WORKFLOW
      workflowRef.value?.render(cloneDeep(workflow))

      return nextTick().then(() => {
        const graphData = getGraphData()
        if (graphData) setSavedWorkflow(graphData)
        workflowRef.value?.fitView()
      })
    })
    .finally(() => {
      loading.value = false
    })
}

/* 退出知识库工作流 */
function goBack() {
  router.push({
    name: 'workspace-knowledge-detail',
    params: { workspaceId, knowledgeId },
  })
}

function handleBack() {
  if (!hasUnsavedChanges()) {
    goBack()
    return
  }

  // 保存失败时保留当前页面，避免丢失尚未写入服务端的画布数据。
  MsgConfirm('提示', '当前工作流尚未保存，是否保存后退出？', {
    cancelButtonText: '直接退出',
    confirmButtonText: '保存并退出',
    confirmButtonType: 'primary',
    distinguishCancelAndClose: true,
  })
    .then(() => {
      return saveKnowledgeWorkflow(undefined, true).then(() => goBack())
    })
    .catch((action: Action) => {
      if (action === 'cancel') goBack()
    })
}

onMounted(() => {
  loadKnowledgeWorkflow().catch(() => {})
})
</script>

<template>
  <WorkflowViewLayout :loading="loading" :title="knowledgeDetail?.name" :save-time="saveTime" @back="handleBack">
    <template #actions>
      <!-- 默认模型设置 -->
      <DefaultModelSettingButton
        :model-value="defaultModelSetting"
        :model-api="ModelApi"
        :get-graph-data="getGraphData"
        :disabled="loading || saving || publishing"
        @save="handleSaveDefaultModelSetting"
        @apply-to-all="handleApplyDefaultModelToAll"
      />
      <!-- 保存 -->
      <el-button plain :loading="saving" :disabled="loading || saving || publishing" @click="handleSave"> 保存 </el-button>
      <!-- 调试 -->
      <el-button type="primary" plain :disabled="loading || saving || publishing" @click="handleDebug"> 调试 </el-button>
      <!-- 发布 -->
      <el-button type="primary" :loading="publishing" :disabled="loading || saving || publishing" @click="handlePublish"> 发布 </el-button>
    </template>

    <WorkflowCanvas
      ref="workflowRef"
      class="min-h-0 flex-1"
      :default-model-settings="defaultModelSetting"
      :loop-workflow-mode="WorkflowMode.KnowledgeLoop"
      :workflow-mode="WorkflowMode.Knowledge"
    />

    <!-- 调试抽屉 -->
    <DebugDrawer ref="debugDrawerRef" :knowledge-id="knowledgeId" />
  </WorkflowViewLayout>
</template>
