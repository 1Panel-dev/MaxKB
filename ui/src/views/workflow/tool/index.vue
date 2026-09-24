<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, provide, ref, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { cloneDeep } from 'lodash'
import { TOOL_TYPE } from '@/api/enums'
import WorkspaceModelApi from '@/api/admin/workspace/model'
import WorkspaceToolApi from '@/api/admin/workspace/tool/tool'
import WorkspaceToolWorkflowApi from '@/api/admin/workspace/tool/workflow'
import SystemModelApi from '@/api/admin/system/resource-management/model'
import SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import SystemToolWorkflowApi from '@/api/admin/system/resource-management/tool/tool-workflow'
import SharedModelApi from '@/api/admin/system/shared-resources/model'
import SharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import SharedToolWorkflowApi from '@/api/admin/system/shared-resources/tool/tool-workflow'
import { getResourceScope, isSystemResource, isSystemSharedResource } from '@/utils/resource-context'
import type { DefaultModelSettingPayload, ToolItem, ToolWorkflowDetail, WorkflowVersion, WorkflowStoreTemplate } from '@/api/types'
import { MsgConfirm, MsgSuccess, MsgError } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultToolNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode } from '@/workflow-canvas/types'
import WorkflowViewLayout from '../components/WorkflowViewLayout.vue'
import ButtonDefaultModelSetting from '@/views/workflow/components/default-model-setting/ButtonDefaultModelSetting.vue'

import ButtonPublishHistory from './ButtonPublishHistory.vue'
import DebugDrawer from './debug/DebugDrawer.vue'
import ButtonTemplateStore from './ButtonTemplateStore.vue'
import { goBack } from './navigation'

defineOptions({ name: 'ToolWorkflowView' })

// 保存、调试与版本历史保持进入页面时的资源范围。
const requestModelApi = isSystemResource() ? SystemModelApi : isSystemSharedResource() ? SharedModelApi : WorkspaceModelApi
const requestToolApi = isSystemResource() ? SystemToolApi : isSystemSharedResource() ? SharedToolApi : WorkspaceToolApi
const requestApi = isSystemResource() ? SystemToolWorkflowApi : isSystemSharedResource() ? SharedToolWorkflowApi : WorkspaceToolWorkflowApi
provide('resourceScope', getResourceScope())

// 为画布节点中的 SelectModel 提供参数表单接口。
provide('getModelParamsForm', requestModelApi.getModelParamsForm)

const DEFAULT_WORKFLOW: LogicFlow.GraphConfigData = {
  nodes: cloneDeep(defaultToolNodes),
  edges: [],
}

const route = useRoute()
const toolId = route.params.toolId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

/* 工具工作流加载与保存 */
const toolDetail = ref<ToolItem>()
const loading = ref(false)
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

function saveToolWorkflow(graphData = getGraphData(), showMessage = false) {
  if (!graphData || historyVisible.value) return Promise.resolve<ToolWorkflowDetail | undefined>(undefined)

  const workflowSnapshot = cloneDeep(graphData)

  return requestApi
    .putToolWorkflow(toolId, { work_flow: workflowSnapshot, default_model_setting: cloneDeep(defaultModelSetting.value) })
    .then((toolWorkflow) => {
      defaultModelSetting.value = cloneDeep(toolWorkflow.default_model_setting ?? {})
      saveTime.value = toolWorkflow.update_time || new Date()
      setSavedWorkflow(workflowSnapshot)
      if (showMessage) MsgSuccess('保存成功')
      return toolWorkflow
    })
}

/* 自动保存：一分钟周期，按资源类型和工具独立记录开关。 */
const AUTO_SAVE_INTERVAL = 60_000
const autoSaveStorageKey = `workflowAutoSave:tool:${toolId}`
const autoSaveEnabled = ref(localStorage.getItem(autoSaveStorageKey) === 'true')
let autoSaveTimer: ReturnType<typeof setInterval> | undefined
const confirmingExit = ref(false)

function stopAutoSave() {
  if (autoSaveTimer !== undefined) clearInterval(autoSaveTimer)
  autoSaveTimer = undefined
}

function startAutoSave() {
  stopAutoSave()
  autoSaveTimer = setInterval(() => {
    if (loading.value || confirmingExit.value || historyVisible.value || !hasUnsavedChanges()) return
    loading.value = true
    saveToolWorkflow()
      .catch(() => {
        // 保存失败保留改动，下个周期继续尝试。
      })
      .finally(() => {
        loading.value = false
      })
  }, AUTO_SAVE_INTERVAL)
}

function handleAutoSaveChange() {
  if (autoSaveEnabled.value) {
    startAutoSave()
    localStorage.setItem(autoSaveStorageKey, 'true')
  } else {
    stopAutoSave()
    localStorage.removeItem(autoSaveStorageKey)
  }
}

/* 调试前保存当前画布，运行参数由基础节点声明。 */
const debugDrawerRef = useTemplateRef<InstanceType<typeof DebugDrawer>>('debugDrawerRef')
async function handleDebug() {
  if (loading.value || historyVisible.value) return
  loading.value = true
  try {
    await workflowRef.value?.validate()
    if (hasUnsavedChanges()) await saveToolWorkflow()
    const graph = getGraphData()
    if (graph) debugDrawerRef.value?.open(graph)
  } catch {
    // 校验与请求错误由各自流程提示，失败时不打开调试。
  } finally {
    loading.value = false
  }
}

function closeDebug() {
  debugDrawerRef.value?.close()
}

/* 模板中心：确认后由服务端替换工作流，再刷新画布与保存基准。 */
const templateStoreButtonRef = useTemplateRef<InstanceType<typeof ButtonTemplateStore>>('templateStoreButtonRef')

function handleUseTemplate(template: WorkflowStoreTemplate) {
  if (loading.value || historyVisible.value) return

  return MsgConfirm('提示', `使用 ${template.name} 将覆盖当前工作流？`, {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  })
    .then(() => {
      loading.value = true
      return requestApi.putToolWorkflow(toolId, { work_flow_template: cloneDeep(template) }).then(() => {
        return loadToolWorkflow().then(() => {
          templateStoreButtonRef.value?.close()
          MsgSuccess('应用成功')
        })
      })
    })
    .catch(() => {
      // 取消或请求失败时保留模板中心，接口错误由请求层提示。
    })
    .finally(() => {
      loading.value = false
    })
}

/* 发布历史：预览保留原草稿，恢复后交由页面保存流程持久化。 */
const historyVisible = ref(false)
const previewVersion = ref<WorkflowVersion>()
let workflowBeforePreview: LogicFlow.GraphData | undefined

function handlePreviewVersion(version: WorkflowVersion) {
  if (loading.value) return
  if (!previewVersion.value) workflowBeforePreview = cloneDeep(getGraphData())
  previewVersion.value = version
  workflowRef.value?.render(cloneDeep(version.work_flow))
  nextTick(() => workflowRef.value?.fitView())
}

// 所有退出入口统一通过显隐状态清理预览；恢复版本时提前清空草稿快照。
watch(historyVisible, (visible) => {
  if (visible) return
  if (workflowBeforePreview) workflowRef.value?.render(cloneDeep(workflowBeforePreview))
  workflowBeforePreview = undefined
  previewVersion.value = undefined
})

function handleRestoreVersion(version = previewVersion.value) {
  if (!version || loading.value) return
  workflowRef.value?.render(cloneDeep(version.work_flow))
  workflowBeforePreview = undefined
  historyVisible.value = false
  nextTick(() => workflowRef.value?.fitView())
}

/* 应用默认模型设置：抽屉提交后暂存，保存失败时从详情回滚。 */
const defaultModelSetting = ref<DefaultModelSettingPayload>({})

function handleApplyDefaultModelToAll(graphData: LogicFlow.GraphData) {
  workflowRef.value?.renderGraphData(graphData)
}

function handleSaveDefaultModelSetting(settings: DefaultModelSettingPayload) {
  defaultModelSetting.value = cloneDeep(settings)
  return handleSave()
}

function handleSave() {
  if (loading.value || historyVisible.value) return
  loading.value = true
  return saveToolWorkflow(undefined, true).finally(() => {
    loading.value = false
  })
}

function handlePublish() {
  if (!workflowRef.value || loading.value || historyVisible.value) return
  loading.value = true
  return workflowRef.value
    .validate()
    .then(() => saveToolWorkflow())
    .then(() => requestApi.putToolWorkflowPublish(toolId))
    .then(() => MsgSuccess('发布成功'))
    .catch(() => {
      MsgError('发布失败')
    })
    .finally(() => {
      loading.value = false
    })
}

/* 导出服务端工作流，先保存当前未提交的画布改动。 */
async function handleExportWorkflow() {
  if (!toolDetail.value || loading.value || historyVisible.value) return
  loading.value = true
  try {
    if (hasUnsavedChanges()) await saveToolWorkflow()
    await requestToolApi.exportTool(toolId, toolDetail.value.name)
  } catch {
    MsgError('导出工作流失败')
  } finally {
    loading.value = false
  }
}

function loadToolWorkflow() {
  return Promise.all([requestToolApi.getToolDetail(toolId), requestApi.getToolWorkflow(toolId)]).then(([tool, toolWorkflow]) => {
    toolDetail.value = tool
    defaultModelSetting.value = cloneDeep(toolWorkflow.default_model_setting ?? {})
    saveTime.value = toolWorkflow.update_time

    const workflow = toolWorkflow.work_flow?.nodes?.length ? toolWorkflow.work_flow : DEFAULT_WORKFLOW
    workflowRef.value?.render(cloneDeep(workflow))

    return nextTick().then(() => {
      const graphData = getGraphData()
      if (graphData) setSavedWorkflow(graphData)
      workflowRef.value?.fitView()
    })
  })
}

/* 退出工具工作流 */
function handleBack() {
  if (loading.value || confirmingExit.value) return
  if (historyVisible.value) {
    historyVisible.value = false
    return
  }
  if (!hasUnsavedChanges()) {
    goBack(toolDetail.value?.folder_id)
    return
  }

  // 保存失败时保留当前页面，避免丢失尚未写入服务端的画布数据。
  confirmingExit.value = true
  MsgConfirm('提示', '当前工作流尚未保存，是否保存后退出？', {
    cancelButtonText: '直接退出',
    confirmButtonText: '保存并退出',
    confirmButtonType: 'primary',
    distinguishCancelAndClose: true,
  })
    .then(() => {
      loading.value = true
      return saveToolWorkflow(undefined, true).then(() => goBack(toolDetail.value?.folder_id))
    })
    .catch((action: Action) => {
      if (action === 'cancel') goBack(toolDetail.value?.folder_id)
    })
    .finally(() => {
      loading.value = false
      confirmingExit.value = false
    })
}

onMounted(() => {
  if (autoSaveEnabled.value) startAutoSave()
  loading.value = true
  loadToolWorkflow()
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
})
onBeforeUnmount(() => stopAutoSave())
</script>

<template>
  <WorkflowViewLayout
    :loading="loading"
    :title="toolDetail?.name"
    :save-time="saveTime"
    :history-visible="historyVisible"
    :can-restore-version="!!previewVersion"
    @back="handleBack"
    @restore-version="handleRestoreVersion()"
  >
    <template #icon>
      <ToolIcon :icon="toolDetail?.icon" :type="toolDetail?.tool_type ?? TOOL_TYPE.WORKFLOW" :size="24" class="shrink-0" />
    </template>
    <template #actions>
      <!-- 模板中心 -->
      <ButtonTemplateStore ref="templateStoreButtonRef" v-model:loading="loading" @open="closeDebug" @use="handleUseTemplate" />
      <!-- 默认模型设置 -->
      <ButtonDefaultModelSetting
        :model-value="defaultModelSetting"
        :model-api="requestModelApi"
        :get-graph-data="getGraphData"
        :disabled="loading"
        @open="closeDebug"
        @save="handleSaveDefaultModelSetting"
        @apply-to-all="handleApplyDefaultModelToAll"
      />

      <!-- 调试工具工作流 -->
      <el-button plain :disabled="loading" @click="handleDebug">
        <MkIcon name="icon_play_outlined" />
        <span>调试</span>
      </el-button>
      <!-- 保存 -->
      <el-button plain :disabled="loading" @click="handleSave">
        <MkIcon name="icon_save_outlined" />
        <span>保存</span>
      </el-button>
      <!-- 发布 -->
      <el-button type="primary" :disabled="loading" @click="handlePublish"> 发布 </el-button>
      <!-- 更多操作 -->
      <MkDropdown trigger="click" placement="bottom-end" class="ml-2" persistent>
        <el-button text class="h-7! w-7! px-0!">
          <MkIcon name="icon_more_outlined" class="rotate-90" :size="20" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu class="w-37">
            <!-- 导出工作流 -->
            <MkDropdownItem @click="handleExportWorkflow">
              <template #icon><MkIcon name="icon_export_outlined" /></template>
              <span>导出工作流</span>
            </MkDropdownItem>
            <!-- 发布历史 -->
            <ButtonPublishHistory
              :api="requestApi"
              v-model:visible="historyVisible"
              :tool-id="toolId"
              :selected-id="previewVersion?.id"
              :disabled="loading"
              @open="closeDebug"
              @preview="handlePreviewVersion"
              @restore="handleRestoreVersion"
            />
            <!-- 自动保存 -->
            <MkDropdownItem @click.stop>
              <template #icon><MkIcon name="icon_save_outlined" /></template>
              <span>自动保存</span>
              <el-switch v-model="autoSaveEnabled" class="ml-auto" size="small" @click.stop @change="handleAutoSaveChange" />
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkDropdown>
    </template>

    <!-- 主画布：历史预览期间禁止编辑。 -->
    <div class="relative min-h-0 flex-1" :inert="!!previewVersion">
      <WorkflowCanvas
        ref="workflowRef"
        class="h-full"
        :default-model-settings="defaultModelSetting"
        :loop-workflow-mode="WorkflowMode.ToolLoop"
        :workflow-mode="WorkflowMode.Tool"
      />
    </div>
    <!-- 调试抽屉 -->
    <DebugDrawer :api="requestApi" ref="debugDrawerRef" :tool-id="toolId" />
  </WorkflowViewLayout>
</template>
