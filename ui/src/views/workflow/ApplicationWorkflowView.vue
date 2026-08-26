<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, provide, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application.ts'
import type { ApplicationDetail } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultNodes, nodeDict } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode, WorkflowNodeType, type ShapeItem } from '@/workflow-canvas/types'
import WorkflowComponentMenu from './components/WorkflowComponentMenu.vue'

defineOptions({ name: 'ApplicationWorkflowView' })

const DEFAULT_WORKFLOW: LogicFlow.GraphConfigData = {
  nodes: structuredClone(defaultNodes),
  edges: [],
}

const route = useRoute()
const router = useRouter()
const applicationId = route.params.applicationId as string
const workspaceId = route.params.workspaceId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

/* 添加工作流组件 */
function toShapeItem(nodeType: WorkflowNodeType): ShapeItem | undefined {
  const node = nodeDict[nodeType]
  if (!node) return

  return {
    type: node.type,
    properties: node.properties,
    text: node.text,
  }
}

function handleAddNode(nodeType: WorkflowNodeType) {
  const shapeItem = toShapeItem(nodeType)
  if (shapeItem) workflowRef.value?.addNode(shapeItem)
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
  savedWorkflow.value = structuredClone(graphData)
}

function hasUnsavedChanges() {
  const graphData = getGraphData()
  if (!graphData || !savedWorkflow.value) return false

  return JSON.stringify(graphData) !== JSON.stringify(savedWorkflow.value)
}

function saveApplication(graphData = getGraphData(), showMessage = false) {
  if (!graphData) return Promise.resolve<ApplicationDetail | undefined>(undefined)

  saving.value = true
  return ApplicationApi.putApplication(applicationId, { work_flow: graphData })
    .then((application) => {
      applicationDetail.value = application
      saveTime.value = application.update_time || new Date()
      setSavedWorkflow(graphData)
      if (showMessage) MsgSuccess('保存成功')
      return application
    })
    .finally(() => {
      saving.value = false
    })
}

function handleSave() {
  saveApplication(undefined, true)
}

function loadApplicationDetail() {
  loading.value = true
  return ApplicationApi.getApplicationDetail(applicationId)
    .then((application) => {
      applicationDetail.value = application
      saveTime.value = application.update_time

      const workflow = application.work_flow?.nodes?.length
        ? application.work_flow
        : DEFAULT_WORKFLOW
      workflowRef.value?.render(structuredClone(workflow))

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
  <main v-loading="loading" class="flex h-screen w-screen flex-col overflow-hidden">
    <header class="h-header flex-between shrink-0 gap-3 border-b bg-white px-6">
      <div class="flex min-w-0 items-center gap-3">
        <el-button text class="-ml-3" @click="handleBack">
          <MkIcon name="icon_left_outlined" :size="18" />
        </el-button>
        <h4 class="max-w-[300px] truncate" :title="applicationDetail?.name">
          {{ applicationDetail?.name }}
        </h4>
        <span v-if="saveTime" class="shrink-0 text-sm text-N600">
          保存于 {{ datetimeFormat(saveTime) }}
        </span>
      </div>

      <div class="flex shrink-0 items-center gap-3">
        <WorkflowComponentMenu @select="handleAddNode" />
        <el-button
          :loading="saving && !publishing"
          :disabled="loading || saving || publishing"
          @click="handleSave"
        >
          保存
        </el-button>
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
      </div>
    </header>
    <!-- 主画布 -->
    <WorkflowCanvas ref="workflowRef" class="min-h-0 flex-1" />
  </main>
</template>
