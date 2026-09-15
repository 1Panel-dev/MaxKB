<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, provide, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { cloneDeep } from 'lodash'
import ApplicationApi from '@/api/admin/workspace/application/application.ts'
import WorkflowVersionApi from '@/api/admin/workspace/application/workflow-version'
import ModelApi from '@/api/admin/workspace/model/model'
import type { ApplicationDetail, ApplicationStoreTemplate, DefaultModelSettingPayload, WorkflowVersion } from '@/api/types'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultApplicationNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode } from '@/workflow-canvas/types'
import ButtonDefaultModelSetting from '../components/default-model-setting/ButtonDefaultModelSetting.vue'
import WorkflowViewLayout from '../components/WorkflowViewLayout.vue'
import ButtonPublishHistory from '../components/publish-history/ButtonPublishHistory.vue'
import TemplateStoreDialog from '@/views/application/template-store/TemplateStoreDialog.vue'
import DebugPanel from './debug/DebugPanel.vue'
import { getResourceScope } from '@/utils/resource-context.ts'
import { goBack } from './navigation'

defineOptions({ name: 'ApplicationWorkflowView' })
provide('resourceScope', getResourceScope())

const DEFAULT_WORKFLOW: LogicFlow.GraphConfigData = {
  nodes: cloneDeep(defaultApplicationNodes),
  edges: [],
}

const route = useRoute()
const applicationId = route.params.applicationId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

/* 智能体工作流加载与保存 */
const applicationDetail = ref<ApplicationDetail>()
const loading = ref(false)
const publishing = ref(false)
const saving = ref(false)
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

function saveApplication(graphData = getGraphData(), showMessage = false) {
  if (!graphData || previewVersion.value) return Promise.resolve<ApplicationDetail | undefined>(undefined)

  // 固定本次提交快照，保留请求期间继续编辑产生的未保存状态。
  const workflowSnapshot = cloneDeep(graphData)
  saving.value = true
  return ApplicationApi.putApplication(applicationId, { work_flow: workflowSnapshot, default_model_setting: cloneDeep(defaultModelSetting.value) })
    .then((application) => {
      applicationDetail.value = application
      defaultModelSetting.value = cloneDeep(application.default_model_setting ?? {})
      saveTime.value = application.update_time || new Date()
      setSavedWorkflow(workflowSnapshot)
      if (showMessage) MsgSuccess('保存成功')
      return application
    })
    .catch((error) => {
      defaultModelSetting.value = cloneDeep(applicationDetail.value?.default_model_setting ?? {})
      MsgError('保存失败')
      throw error
    })
    .finally(() => {
      saving.value = false
    })
}

function handleSave() {
  return saveApplication(undefined, true)
}

/* 自动保存：一分钟周期，按资源类型和智能体独立记录开关。 */
const AUTO_SAVE_INTERVAL = 60_000
const autoSaveStorageKey = `workflowAutoSave:application:${applicationId}`
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
    if (loading.value || saving.value || publishing.value || confirmingExit.value || historyVisible.value || !hasUnsavedChanges()) return
    saveApplication()
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

/* 调试入口 */
const debugPanelRef = useTemplateRef<InstanceType<typeof DebugPanel>>('debugPanelRef')

function handleDebug() {
  if (loading.value || saving.value) return
  if (!hasUnsavedChanges()) {
    debugPanelRef.value?.open()
    return
  }
  // 调试前先保存，失败时保留面板原有状态。
  return saveApplication()
    .then(() => {
      debugPanelRef.value?.open()
    })
    .catch(() => {
      /* 保存失败已由保存流程提示。 */
    })
}

function closeDebug() {
  debugPanelRef.value?.close()
}

/* 发布历史：预览保留原草稿，恢复后交由页面保存流程持久化。 */
const historyVisible = ref(false)
const previewVersion = ref<WorkflowVersion>()
let workflowBeforePreview: LogicFlow.GraphData | undefined

function handlePreviewVersion(version: WorkflowVersion) {
  if (loading.value || saving.value || publishing.value) return
  if (!previewVersion.value) workflowBeforePreview = cloneDeep(getGraphData())
  previewVersion.value = version
  workflowRef.value?.render(cloneDeep(version.work_flow))
  nextTick(() => workflowRef.value?.fitView())
}

function handleCloseHistory() {
  if (workflowBeforePreview) workflowRef.value?.render(cloneDeep(workflowBeforePreview))
  workflowBeforePreview = undefined
  previewVersion.value = undefined
  historyVisible.value = false
}

function handleRestoreVersion(version = previewVersion.value) {
  if (!version || loading.value || saving.value || publishing.value) return
  workflowRef.value?.render(cloneDeep(version.work_flow))
  workflowBeforePreview = undefined
  previewVersion.value = undefined
  historyVisible.value = false
  nextTick(() => workflowRef.value?.fitView())
}

function handleUpdateVersion(version: WorkflowVersion) {
  if (previewVersion.value?.id === version.id) previewVersion.value = version
}

/* 模板中心 */
const templateStoreDialogRef = useTemplateRef<InstanceType<typeof TemplateStoreDialog>>('templateStoreDialogRef')

function handleOpenTemplateStore() {
  if (loading.value || saving.value || publishing.value) return
  closeDebug()
  templateStoreDialogRef.value?.open()
}

function handleUseTemplate(template: ApplicationStoreTemplate) {
  if (loading.value || saving.value || publishing.value) return
  saving.value = true
  return MsgConfirm('提示', `使用 ${template.name} 将覆盖当前工作流？`, {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  })
    .then(() => {
      return ApplicationApi.putApplication(applicationId, { work_flow_template: cloneDeep(template) }).then(() => {
        // 重新加载服务端模板，更新画布和已保存基准。
        return loadApplicationDetail().then(() => {
          templateStoreDialogRef.value?.close()
          MsgSuccess('应用成功')
        })
      })
    })
    .catch(() => {
      // 取消或请求失败时保留模板中心，接口错误由请求层提示。
    })
    .finally(() => {
      saving.value = false
    })
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

/* 发布工作流 */
function handlePublish() {
  workflowRef.value?.validate().then(() => {
    // publishing.value = true
    // return saveApplication(undefined, false)
    //   .then(() => ApplicationApi.putApplicationPublish(applicationId))
    //   .then((application) => {
    //     applicationDetail.value = application
    //     saveTime.value = application.update_time || saveTime.value
    //     MsgSuccess('发布成功')
    //   })
    //   .finally(() => {
    //     publishing.value = false
    //   })
  })
}

/* 退出工作流 */
function handleBack() {
  if (loading.value || saving.value || confirmingExit.value) return
  if (historyVisible.value) {
    handleCloseHistory()
    return
  }
  if (!hasUnsavedChanges()) {
    goBack(applicationId)
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
      return saveApplication(undefined, true).then(() => goBack(applicationId))
    })
    .catch((action: Action) => {
      if (action === 'cancel') goBack(applicationId)
    })
    .finally(() => {
      confirmingExit.value = false
    })
}

// 加载详情
function loadApplicationDetail() {
  loading.value = true
  return ApplicationApi.getApplicationDetail(applicationId)
    .then((application) => {
      applicationDetail.value = application
      defaultModelSetting.value = cloneDeep(application.default_model_setting ?? {})
      saveTime.value = application.update_time

      const workflow = application.work_flow?.nodes?.length ? application.work_flow : DEFAULT_WORKFLOW
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

onMounted(() => {
  if (autoSaveEnabled.value) startAutoSave()
  loadApplicationDetail()
})

onBeforeUnmount(() => stopAutoSave())
</script>

<template>
  <WorkflowViewLayout
    :loading="loading"
    :title="applicationDetail?.name"
    :save-time="saveTime"
    :history-visible="historyVisible"
    :can-restore-version="!!previewVersion && !loading && !saving && !publishing"
    @back="handleBack"
    @restore-version="handleRestoreVersion()"
  >
    <template #icon>
      <ApplicationIcon :icon="applicationDetail?.icon" :size="32" class="shrink-0" />
    </template>
    <template #actions>
      <!-- 模板中心 -->
      <el-button plain :disabled="loading || saving || publishing" @click="handleOpenTemplateStore">
        <MkIcon name="icon_template_outlined" />
        <span>模板中心</span>
      </el-button>

      <!-- 默认模型设置 -->
      <ButtonDefaultModelSetting
        :model-value="defaultModelSetting"
        :model-api="ModelApi"
        :get-graph-data="getGraphData"
        :disabled="loading || saving || publishing"
        @open="closeDebug"
        @save="handleSaveDefaultModelSetting"
        @apply-to-all="handleApplyDefaultModelToAll"
      />

      <!-- 调试 -->
      <el-button plain :disabled="loading || saving" @click="handleDebug">
        <MkIcon name="icon_play_outlined" />
        <span>调试</span>
      </el-button>

      <!-- 保存 -->
      <el-button plain :disabled="loading || saving || publishing" @click="handleSave()">
        <MkIcon name="icon_save_outlined" />
        <span> 保存 </span>
      </el-button>

      <!-- 发布 -->
      <el-button type="primary" :disabled="loading || saving || publishing" @click="handlePublish"> 发布 </el-button>
      <!-- 更多操作 -->
      <MkDropdown trigger="click" placement="bottom-end" class="ml-2" persistent>
        <el-button text class="h-7! w-7! px-0!">
          <MkIcon name="icon_more_outlined" class="rotate-90" :size="20" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu class="w-37">
            <!-- 去对话 -->
            <MkDropdownItem>
              <template #icon><MkIcon name="icon_new-chat_outlined" /></template>
              <span>去对话</span>
            </MkDropdownItem>
            <!-- 发布历史 -->
            <ButtonPublishHistory
              v-model:visible="historyVisible"
              :resource-id="applicationId"
              :api="WorkflowVersionApi"
              :selected-id="previewVersion?.id"
              :disabled="loading || saving || publishing"
              @open="closeDebug"
              @preview="handlePreviewVersion"
              @restore="handleRestoreVersion"
              @update="handleUpdateVersion"
              @close="handleCloseHistory"
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
    <!-- 主画布 -->
    <div class="relative flex min-h-0 flex-1">
      <div class="relative min-w-0 flex-1" :inert="!!previewVersion">
        <WorkflowCanvas
          ref="workflowRef"
          class="h-full"
          :default-model-settings="defaultModelSetting"
          :loop-workflow-mode="WorkflowMode.ApplicationLoop"
          :workflow-mode="WorkflowMode.Application"
        />
      </div>
    </div>

    <!-- 调试框 -->
    <DebugPanel ref="debugPanelRef" />
    <!-- 模版中心 -->
    <TemplateStoreDialog ref="templateStoreDialogRef" source="work_flow" :applying="saving" @use="handleUseTemplate" />
  </WorkflowViewLayout>
</template>
