<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, provide, ref, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { cloneDeep } from 'lodash'
import ApplicationApi from '@/api/admin/workspace/application/application.ts'
import ModelApi from '@/api/admin/workspace/model'
import type { ApplicationDetail, ApplicationStoreTemplate, DefaultModelSettingPayload, WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultApplicationNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode } from '@/workflow-canvas/types'
import ButtonDefaultModelSetting from '../components/default-model-setting/ButtonDefaultModelSetting.vue'
import WorkflowViewLayout from '../components/WorkflowViewLayout.vue'
import ButtonPublishHistory from './ButtonPublishHistory.vue'
import ButtonTemplateStore from './ButtonTemplateStore.vue'
import DebugPanel from '@/conversation-panel/view/debug/index.vue'
import EditPublishVersionDialog from '../components/publish-history/EditPublishVersionDialog.vue'
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
}

function handleSave() {
  if (loading.value || historyVisible.value) return
  loading.value = true
  return saveApplication(undefined, true).finally(() => {
    loading.value = false
  })
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
    if (loading.value || confirmingExit.value || historyVisible.value || !hasUnsavedChanges()) return
    loading.value = true
    saveApplication()
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

/* 调试入口 */
const debugPanelRef = useTemplateRef<InstanceType<typeof DebugPanel>>('debugPanelRef')

async function handleDebug() {
  if (loading.value || historyVisible.value) return
  loading.value = true
  try {
    if (hasUnsavedChanges()) await saveApplication()
    debugPanelRef.value?.open()
  } catch {
    // 保存失败已由保存流程提示。
  } finally {
    loading.value = false
  }
}

function closeDebug() {
  debugPanelRef.value?.close()
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

/* 模板中心 */
const templateStoreButtonRef = useTemplateRef<InstanceType<typeof ButtonTemplateStore>>('templateStoreButtonRef')

function handleUseTemplate(template: ApplicationStoreTemplate) {
  if (loading.value) return

  return MsgConfirm('提示', `使用 ${template.name} 将覆盖当前工作流？`, {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  })
    .then(() => {
      loading.value = true
      return ApplicationApi.putApplication(applicationId, { work_flow_template: cloneDeep(template) }).then(() => {
        // 重新加载服务端模板，更新画布和已保存基准。
        return loadApplicationDetail().then(() => {
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

/* 应用默认模型设置：抽屉提交后暂存，保存失败时从详情回滚。 */
const defaultModelSetting = ref<DefaultModelSettingPayload>({})

function handleApplyDefaultModelToAll(graphData: LogicFlow.GraphData) {
  workflowRef.value?.renderGraphData(graphData)
}

function handleSaveDefaultModelSetting(settings: DefaultModelSettingPayload) {
  defaultModelSetting.value = cloneDeep(settings)
  return handleSave()
}

/* 发布工作流：先校验画布，再填写发布内容，提交后保存并发布。 */
const publishDialogRef = useTemplateRef<InstanceType<typeof EditPublishVersionDialog>>('publishDialogRef')

function handleOpenPublish() {
  if (loading.value || historyVisible.value || !workflowRef.value) return
  loading.value = true
  return workflowRef.value
    .validate()
    .then(() => {
      closeDebug()
      publishDialogRef.value?.open()
    })
    .catch(() => {
      // 画布校验失败时保留编辑态，错误由画布提示。
    })
    .finally(() => {
      loading.value = false
    })
}

function handlePublish(payload: WorkflowVersionPayload) {
  if (loading.value || historyVisible.value || !workflowRef.value) return
  loading.value = true
  return saveApplication()
    .then(() => ApplicationApi.putApplicationPublish(applicationId, payload.name, payload.publish_desc))
    .then((application) => {
      applicationDetail.value = application
      saveTime.value = application.update_time || saveTime.value
      publishDialogRef.value?.close()
      MsgSuccess('发布成功')
    })
    .finally(() => {
      loading.value = false
    })
}

/* 退出工作流 */
function handleBack() {
  if (loading.value || confirmingExit.value) return
  if (historyVisible.value) {
    historyVisible.value = false
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
      loading.value = true
      return saveApplication(undefined, true).then(() => goBack(applicationId))
    })
    .catch((action: Action) => {
      if (action === 'cancel') goBack(applicationId)
    })
    .finally(() => {
      loading.value = false
      confirmingExit.value = false
    })
}

// 加载详情
function loadApplicationDetail() {
  return ApplicationApi.getApplicationDetail(applicationId).then((application) => {
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
}

onMounted(() => {
  if (autoSaveEnabled.value) startAutoSave()
  loading.value = true
  loadApplicationDetail()
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
    :title="applicationDetail?.name"
    :save-time="saveTime"
    :history-visible="historyVisible"
    :can-restore-version="!!previewVersion"
    @back="handleBack"
    @restore-version="handleRestoreVersion()"
  >
    <template #icon>
      <ApplicationIcon :icon="applicationDetail?.icon" :size="32" class="shrink-0" />
    </template>
    <template #actions>
      <!-- 模板中心 -->
      <ButtonTemplateStore ref="templateStoreButtonRef" v-model:loading="loading" @open="closeDebug" @use="handleUseTemplate" />

      <!-- 默认模型设置 -->
      <ButtonDefaultModelSetting
        :model-value="defaultModelSetting"
        :model-api="ModelApi"
        :get-graph-data="getGraphData"
        :disabled="loading"
        @open="closeDebug"
        @save="handleSaveDefaultModelSetting"
        @apply-to-all="handleApplyDefaultModelToAll"
      />

      <!-- 调试 -->
      <el-button plain :disabled="loading" @click="handleDebug">
        <MkIcon name="icon_play_outlined" />
        <span>调试</span>
      </el-button>

      <!-- 保存 -->
      <el-button plain :disabled="loading" @click="handleSave()">
        <MkIcon name="icon_save_outlined" />
        <span> 保存 </span>
      </el-button>

      <!-- 发布 -->
      <el-button type="primary" :disabled="loading" @click="handleOpenPublish">发布</el-button>
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
              :application-id="applicationId"
              :selected-id="previewVersion?.id"
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
    <!-- 主画布 -->
    <div class="relative min-h-0 min-w-0 flex-1" :inert="!!previewVersion">
      <WorkflowCanvas
        ref="workflowRef"
        class="h-full"
        :default-model-settings="defaultModelSetting"
        :loop-workflow-mode="WorkflowMode.ApplicationLoop"
        :workflow-mode="WorkflowMode.Application"
      />
    </div>

    <!-- 调试框 -->
    <DebugPanel ref="debugPanelRef" />
    <!-- 发布内容 -->
    <EditPublishVersionDialog ref="publishDialogRef" mode="publish" :saving="loading" @submit="handlePublish" />
  </WorkflowViewLayout>
</template>
