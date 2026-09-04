<script setup lang="ts">
import { nextTick, onMounted, provide, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { Aim, Close, FullScreen } from '@element-plus/icons-vue'
import { cloneDeep } from 'lodash'
import ApplicationApi from '@/api/admin/workspace/application/application.ts'
import ModelApi from '@/api/admin/workspace/model/model'
import type { ApplicationDetail } from '@/api/types'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultApplicationNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode, type ShapeItem } from '@/workflow-canvas/types'
import DefaultModelSettingButton from './components/default-model-setting/DefaultModelSettingButton.vue'
import CreateNodeMenu from './components/CreateNodeMenu.vue'
import WorkflowViewLayout from './components/WorkflowViewLayout.vue'
import Conversation from '@/components/conversation/index.vue'

defineOptions({ name: 'ApplicationWorkflowView' })

// 为画布节点中的 ModelSelect 提供参数表单接口。
provide('getModelParamsForm', ModelApi.getModelParamsForm)

const DEFAULT_WORKFLOW: LogicFlow.GraphConfigData = {
  nodes: cloneDeep(defaultApplicationNodes),
  edges: [],
}

const route = useRoute()
const router = useRouter()
const applicationId = route.params.applicationId as string
const workspaceId = route.params.workspaceId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

/* 添加工作流组件 */
function handleAddNode(shapeItem: ShapeItem) {
  workflowRef.value?.addNode(shapeItem)
}

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
  if (!graphData) return Promise.resolve<ApplicationDetail | undefined>(undefined)

  saving.value = true
  return ApplicationApi.putApplication(applicationId, { work_flow: graphData, default_model_setting: cloneDeep(defaultModelSetting.value) })
    .then((application) => {
      applicationDetail.value = application
      defaultModelSetting.value = cloneDeep(application.default_model_setting ?? {})
      saveTime.value = application.update_time || new Date()
      setSavedWorkflow(graphData)
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
  // 保存失败已提示并回滚，页面按钮在此结束处理。
  return saveApplication(undefined, true).catch(() => {})
}

/* 应用默认模型设置：抽屉提交后暂存，保存失败时从详情回滚。 */
const defaultModelSetting = ref<NonNullable<ApplicationDetail['default_model_setting']>>({})

function handleApplyDefaultModelToAll(graphData: LogicFlow.GraphData) {
  workflowRef.value?.renderGraphData(graphData)
}

function handleSaveDefaultModelSetting(settings: NonNullable<ApplicationDetail['default_model_setting']>) {
  defaultModelSetting.value = cloneDeep(settings)
  return handleSave()
}

/* 调试对话 */
const debugVisible = ref(false)
const debugExpanded = ref(false)

function closeDebug() {
  debugVisible.value = false
  debugExpanded.value = false
}

function handleDebug() {
  // 未保存的画布改动先落库，保证调试对话命中最新的工作流。
  if (hasUnsavedChanges()) {
    return saveApplication(undefined, false)
      .then(() => {
        debugVisible.value = true
      })
      .catch(() => {})
  }
  debugVisible.value = true
}

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

/* 发布工作流 */
// const canPublish = computed(() => perm.application.workspace.publish(applicationId))
// function getValidationMessage(error: unknown) {
//   if (typeof error === 'string') return error
//   if (error instanceof Error) return error.message
//   if (!error || typeof error !== 'object') return '工作流校验失败'

//   const validationError = error as {
//     errMessage?: unknown
//     node?: { properties?: { stepName?: string } }
//   }
//   const stepName = validationError.node?.properties?.stepName
//   const message =
//     typeof validationError.errMessage === 'string' ? validationError.errMessage : '工作流配置不完整'

//   return stepName ? `${stepName} 节点，${message}` : message
// }

// function validateWorkflow() {
//   const graphData = getGraphData()
//   if (!graphData) return Promise.resolve<LogicFlow.GraphData | undefined>(undefined)

//   return (workflowRef.value?.validate() ?? Promise.resolve([]))
//     .then(() => {
//       type ValidationGraph = ConstructorParameters<typeof WorkFlowInstance>[0]
//       new WorkFlowInstance(graphData as unknown as ValidationGraph).is_valid()
//       return graphData
//     })
//     .catch((error: unknown) => {
//       MsgError(getValidationMessage(error))
//       return undefined
//     })
// }

// function handlePublish() {
//   validateWorkflow().then((graphData) => {
//     if (!graphData) return

//     publishing.value = true
//     return saveApplication(graphData)
//       .then(() => ApplicationApi.putApplicationPublish(applicationId))
//       .then((application) => {
//         applicationDetail.value = application
//         saveTime.value = application.update_time || saveTime.value
//         MsgSuccess('发布成功')
//       })
//       .finally(() => {
//         publishing.value = false
//       })
//   })
// }

/* 自动保存 */
// const AUTO_SAVE_INTERVAL = 60_000
// const AUTO_SAVE_STORAGE_KEY = 'workflowAutoSave'
// const autoSaveEnabled = ref(localStorage.getItem(AUTO_SAVE_STORAGE_KEY) === 'true')
// let autoSaveTimer: ReturnType<typeof setInterval> | undefined

// function stopAutoSave() {
//   if (autoSaveTimer) clearInterval(autoSaveTimer)
//   autoSaveTimer = undefined
// }

// function startAutoSave() {
//   stopAutoSave()
//   if (!canEdit.value) return

//   autoSaveTimer = setInterval(() => {
//     if (
//       canEdit.value &&
//       !loading.value &&
//       !saving.value &&
//       !publishing.value &&
//       hasUnsavedChanges()
//     ) {
//       saveApplication()
//     }
//   }, AUTO_SAVE_INTERVAL)
// }

// function handleAutoSaveChange(value: string | number | boolean) {
//   autoSaveEnabled.value = Boolean(value)
//   localStorage.setItem(AUTO_SAVE_STORAGE_KEY, String(autoSaveEnabled.value))
//   if (autoSaveEnabled.value) startAutoSave()
//   else stopAutoSave()
// }

/* 退出工作流 */
function goBack() {
  router.push({ name: 'workspace-application-list', params: { workspaceId } })
}

function handleBack() {
  if (!hasUnsavedChanges()) {
    goBack()
    return
  }

  // 保存失败时保留当前页面，避免丢失尚未写入服务端的画布数据。
  MsgConfirm('当前工作流尚未保存，是否保存后退出？', undefined, {
    cancelButtonText: '直接退出',
    confirmButtonText: '保存并退出',
    confirmButtonType: 'primary',
    distinguishCancelAndClose: true,
  })
    .then(() => {
      return saveApplication(undefined, true).then(() => goBack())
    })
    .catch((action: Action) => {
      if (action === 'cancel') goBack()
    })
}

onMounted(() => {
  loadApplicationDetail().then(() => {
    // if (autoSaveEnabled.value && canEdit.value) startAutoSave()
  })
})

// onBeforeUnmount(() => stopAutoSave())
</script>

<template>
  <WorkflowViewLayout :loading="loading" :title="applicationDetail?.name" :save-time="saveTime" @back="handleBack">
    <template #actions>
      <CreateNodeMenu :workflow-mode="WorkflowMode.Application" @select="handleAddNode" />
      <DefaultModelSettingButton
        :model-value="defaultModelSetting"
        :model-api="ModelApi"
        :get-graph-data="getGraphData"
        :disabled="loading || saving || publishing"
        @save="handleSaveDefaultModelSetting"
        @apply-to-all="handleApplyDefaultModelToAll"
      />
      <el-button plain :loading="saving && !publishing" :disabled="loading || saving || publishing" @click="handleSave()"> 保存 </el-button>
      <el-button type="primary" plain :disabled="loading || saving" @click="handleDebug"> 调试 </el-button>
      <!-- <el-button
        v-if="canPublish"
        type="primary"
        :loading="publishing"
        :disabled="loading || saving || publishing"
        @click="handlePublish"
      >
        发布
      </el-button>

      <MkDropdown v-if="canEdit" trigger="click">
        <el-button text aria-label="更多工作流设置">
          <MkIcon :icon="MoreFilled" :size="18" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu>
            <MkDropdownItem @click.stop>
              <span>自动保存</span>
              <el-switch
                v-model="autoSaveEnabled"
                size="small"
                @click.stop
                @change="handleAutoSaveChange"
              />
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkDropdown>
  -->
    </template>
    <!-- 主画布 -->
    <WorkflowCanvas
      ref="workflowRef"
      class="min-h-0 flex-1"
      :default-model-settings="defaultModelSetting"
      :loop-workflow-mode="WorkflowMode.ApplicationLoop"
      :workflow-mode="WorkflowMode.Application"
    />

    <!-- 调试对话：右侧悬浮面板 -->
    <transition name="debug-panel">
      <div v-if="debugVisible" class="workflow-debug-panel" :class="{ expanded: debugExpanded }">
        <div class="debug-panel-actions">
          <button type="button" class="debug-panel-btn" :aria-label="debugExpanded ? '还原' : '放大'" @click="debugExpanded = !debugExpanded">
            <MkIcon :icon="debugExpanded ? Aim : FullScreen" :size="16" />
          </button>
          <button type="button" class="debug-panel-btn" aria-label="关闭调试" @click="closeDebug">
            <MkIcon :icon="Close" :size="16" />
          </button>
        </div>
        <Conversation :defaultOpen="false" type="DEBUG" class="h-full" />
      </div>
    </transition>
  </WorkflowViewLayout>
</template>

<style scoped>
.workflow-debug-panel {
  position: absolute;
  top: calc(var(--mk-header-height) + 12px);
  right: 12px;
  bottom: 12px;
  width: 460px;
  max-width: calc(100vw - 24px);
  z-index: 20;
  background: var(--mk-N0, #fff);
  border: 1px solid var(--mk-N200, #dcdfe6);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  transition:
    width 0.25s ease,
    top 0.25s ease,
    right 0.25s ease,
    bottom 0.25s ease,
    border-radius 0.25s ease;
}

/* 放大：宽度占视口 50%，高度 100% */
.workflow-debug-panel.expanded {
  top: 0;
  right: 0;
  bottom: 0;
  width: 50vw;
  max-width: 100vw;
  border-radius: 0;
}

/* 面板内的对话框自带移动端样式：小屏下会把输入框 fixed 到整个视口。
   这里把它约束回面板内部，避免输入框脱离面板铺满视口。 */
.workflow-debug-panel :deep(.panel-input) {
  position: relative !important;
  left: auto !important;
  right: auto !important;
  bottom: auto !important;
}

.debug-panel-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 4px;
}

.debug-panel-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--mk-N600, #606266);
  cursor: pointer;
}
.debug-panel-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.debug-panel-enter-active,
.debug-panel-leave-active {
  transition:
    transform 0.25s ease,
    opacity 0.25s ease;
}
.debug-panel-enter-from,
.debug-panel-leave-to {
  transform: translateX(16px);
  opacity: 0;
}
</style>
