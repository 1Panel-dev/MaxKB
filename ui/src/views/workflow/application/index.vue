<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, provide, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ApplicationDetail, ApplicationStoreTemplate, DefaultModelSettingPayload, WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import type { ApiInputField } from '@/workflow-canvas/nodes/base-node/types'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import SystemResourceWorkflowApi from '@/api/admin/system/resource-management/application/workflow'
import SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import WorkspaceApplicationApi from '@/api/admin/workspace/application/application'
import WorkspaceWorkflowApi from '@/api/admin/workspace/application/workflow'
import WorkspaceModelApi from '@/api/admin/workspace/model'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { defaultApplicationNodes } from '@/workflow-canvas/config/node-mapping'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import WorkflowViewLayout from '../components/WorkflowViewLayout.vue'
import ButtonDefaultModelSetting from '../components/default-model-setting/ButtonDefaultModelSetting.vue'
import EditPublishVersionDialog from '../components/publish-history/EditPublishVersionDialog.vue'
import { showWorkflowValidateError } from '../components/validate-error'
import ButtonAiGenerate from './components/ButtonAiGenerate.vue'
import ButtonDebug from './components/ButtonDebug.vue'
import ButtonPublishHistory from './components/ButtonPublishHistory.vue'
import ButtonTemplateStore from './components/ButtonTemplateStore.vue'
import { goBack } from './navigation'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import { getResourceScope, isSystemResource } from '@/utils/resource-context.ts'
import perm from '@/permission/index.ts'

type ApplicationWorkflowPermissionMethod = 'publish' | 'edit'
function applicationWorkflowPermission(method: ApplicationWorkflowPermissionMethod): boolean {
  if (isSystemResource()) return Boolean(perm.application.system[method]())
  return Boolean(perm.application.workspace[method](applicationId))
}

defineOptions({ name: 'ApplicationWorkflowView' })
const { t } = useI18n({ useScope: 'global' })
const requestApi = isSystemResource() ? SystemResourceApplicationApi : WorkspaceApplicationApi
const requestModelApi = isSystemResource() ? SystemResourceModelApi : WorkspaceModelApi
const requestWorkflowApi = isSystemResource() ? SystemResourceWorkflowApi : WorkspaceWorkflowApi
provide('resourceScope', getResourceScope())
provide('getModelParamsForm', requestModelApi.getModelParamsForm)

const DEFAULT_WORKFLOW: LogicFlow.GraphConfigData = {
  nodes: cloneDeep(defaultApplicationNodes),
  edges: [],
}

const route = useRoute()
const applicationId = route.params.applicationId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

/* 智能体工作流加载与保存 */
const applicationDetail = ref<ApplicationDetail>()
provide(
  'resourceWorkspaceId',
  computed(() => applicationDetail.value?.workspace_id),
)
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
  return requestApi
    .putApplication(applicationId, { work_flow: workflowSnapshot, default_model_setting: cloneDeep(defaultModelSetting.value) })
    .then((application) => {
      applicationDetail.value = application
      defaultModelSetting.value = cloneDeep(application.default_model_setting ?? {})
      saveTime.value = application.update_time || new Date()
      setSavedWorkflow(workflowSnapshot)
      if (showMessage) MsgSuccess(t('common.messages.saveSuccess'))
      return application
    })
    .catch((error) => {
      defaultModelSetting.value = cloneDeep(applicationDetail.value?.default_model_setting ?? {})
      MsgError(t('workflow.layout.saveFailed'))
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
const debugButtonRef = useTemplateRef<InstanceType<typeof ButtonDebug>>('debugButtonRef')

function validateWorkflow() {
  if (!workflowRef.value) return Promise.reject(new Error(t('workflow.layout.canvasNotLoaded')))
  return workflowRef.value.validate()
}

function closeDebug() {
  debugButtonRef.value?.close()
}

/* 去对话：访问地址与接口传参默认值。 */
const apiQuery = computed(() => {
  const query = applicationDetail.value?.work_flow?.nodes
    ?.find((n) => n.id === WorkflowNodeType.Base)
    ?.properties?.api_input_field_list?.map((field: ApiInputField) => {
      return `${field.variable}=${field.default_value}`
    })
    .join('&')
  if (query) {
    return '?' + query
  }
  return ''
})

const chatBasePath = CHAT_API_BASE_PATH.replace(/\/api$/, '')

function toChat() {
  if (!applicationDetail.value) return
  return requestApi.getAccessToken(applicationId).then((ok) => {
    if (!ok.access_token) return
    const accessUrl = `${window.location.origin}${chatBasePath}/${ok.access_token}/${apiQuery.value}`
    window.open(accessUrl, '_blank')
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

// 抽屉显隐和页面返回统一处理预览；恢复版本时提前清空草稿快照。
function handleHistoryVisibleChange(visible: boolean) {
  historyVisible.value = visible
  if (visible) return
  if (workflowBeforePreview) workflowRef.value?.render(cloneDeep(workflowBeforePreview))
  workflowBeforePreview = undefined
  previewVersion.value = undefined
}

function handleRestoreVersion(version = previewVersion.value) {
  if (!version || loading.value) return
  workflowRef.value?.render(cloneDeep(version.work_flow))
  workflowBeforePreview = undefined
  handleHistoryVisibleChange(false)
  nextTick(() => workflowRef.value?.fitView())
}

/* 模板中心 */
const templateStoreButtonRef = useTemplateRef<InstanceType<typeof ButtonTemplateStore>>('templateStoreButtonRef')

function handleUseTemplate(template: ApplicationStoreTemplate) {
  if (loading.value) return

  return MsgConfirm(t('common.dialogs.notice'), t('workflow.layout.overwriteMessage', { name: template.name }), {
    confirmButtonText: t('common.actions.comfirm'),
    confirmButtonType: 'primary',
  })
    .then(() => {
      loading.value = true
      return requestApi.putApplication(applicationId, { work_flow_template: cloneDeep(template) }).then(() => {
        // 重新加载服务端模板，更新画布和已保存基准。
        return loadApplicationDetail().then(() => {
          templateStoreButtonRef.value?.close()
          MsgSuccess(t('workflow.layout.applySuccess'))
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
    .catch(showWorkflowValidateError)
    .finally(() => {
      loading.value = false
    })
}

function handlePublish(payload: WorkflowVersionPayload) {
  if (loading.value || historyVisible.value || !workflowRef.value) return
  loading.value = true
  return saveApplication()
    .then(() => requestApi.putApplicationPublish(applicationId, payload.name, payload.publish_desc))
    .then((application) => {
      applicationDetail.value = application
      saveTime.value = application.update_time || saveTime.value
      publishDialogRef.value?.close()
      MsgSuccess(t('common.messages.publishSuccess'))
    })
    .finally(() => {
      loading.value = false
    })
}

/* 退出工作流 */
function handleBack() {
  if (loading.value || confirmingExit.value) return
  if (historyVisible.value) {
    handleHistoryVisibleChange(false)
  }
  if (!hasUnsavedChanges()) {
    goBack(applicationId)
    return
  }

  // 保存失败时保留当前页面，避免丢失尚未写入服务端的画布数据。
  confirmingExit.value = true
  MsgConfirm(t('common.dialogs.notice'), t('workflow.layout.unsavedExitMessage'), {
    cancelButtonText: t('workflow.layout.exitDirectly'),
    confirmButtonText: t('workflow.layout.saveAndExit'),
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
  return requestApi.getApplicationDetail(applicationId).then((application) => {
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
      <!-- AI 生成工作流 -->
      <ButtonAiGenerate
        :label="t('workflow.layout.aiGenerate')"
        :disabled="loading || historyVisible"
        :get-logic-flow="() => workflowRef?.getLogicFlow()"
        :default-model-settings="defaultModelSetting"
        @open="closeDebug"
      />

      <!-- 模板中心 -->
      <ButtonTemplateStore
        :label="t('resource.templateStore.title')"
        ref="templateStoreButtonRef"
        v-model:loading="loading"
        @open="closeDebug"
        @use="handleUseTemplate"
      />

      <!-- 默认模型设置 -->
      <ButtonDefaultModelSetting
        :label="t('workflow.defaultModel.settingsTitle')"
        :model-value="defaultModelSetting"
        :model-api="requestModelApi"
        :get-graph-data="getGraphData"
        :disabled="loading"
        @open="closeDebug"
        @save="handleSaveDefaultModelSetting"
        @apply-to-all="handleApplyDefaultModelToAll"
      />

      <!-- 调试 -->
      <ButtonDebug
        ref="debugButtonRef"
        v-model:loading="loading"
        :label="t('common.actions.debug')"
        :disabled="historyVisible"
        :has-unsaved-changes="hasUnsavedChanges"
        :validate-workflow="validateWorkflow"
        :save-workflow="saveApplication"
        :application="applicationDetail"
      />

      <!-- 保存 -->
      <MkTooltip :content="t('common.actions.save')" placement="bottom" v-if="applicationWorkflowPermission('edit')">
        <el-button plain :disabled="loading" @click="handleSave()" class="w-8! min-w-8!">
          <MkIcon name="icon_save_outlined" />
        </el-button>
      </MkTooltip>

      <!-- 发布 -->
      <el-button v-if="applicationWorkflowPermission('publish')" type="primary" :disabled="loading" @click="handleOpenPublish">
        {{ t('common.actions.publish') }}
      </el-button>
      <!-- 更多操作 -->
      <MkDropdown trigger="click" placement="bottom-end" class="ml-2" persistent>
        <el-button text class="h-7! w-7! px-0!">
          <MkIcon name="icon_more_outlined" class="rotate-90" :size="20" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu>
            <!-- 去对话 -->
            <MkDropdownItem @click="toChat">
              <template #icon><MkIcon name="icon_new-chat_outlined" /></template>
              <span>{{ t('application.actions.chat') }}</span>
            </MkDropdownItem>
            <!-- 发布历史 -->
            <ButtonPublishHistory
              :label="t('workflow.publishHistory.title')"
              :api="requestWorkflowApi"
              :visible="historyVisible"
              @update:visible="handleHistoryVisibleChange"
              :application-id="applicationId"
              :selected-id="previewVersion?.id"
              @open="closeDebug"
              @preview="handlePreviewVersion"
              @restore="handleRestoreVersion"
            />
            <!-- 自动保存 -->
            <MkDropdownItem @click.stop>
              <template #icon><MkIcon name="icon_save_outlined" /></template>
              <span>{{ t('workflow.layout.autoSave') }}</span>
              <el-switch v-model="autoSaveEnabled" class="ml-auto" size="small" @click.stop @change="handleAutoSaveChange" />
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkDropdown>
    </template>
    <!-- 主画布 -->
    <div class="relative min-h-0 min-w-0 flex-1">
      <WorkflowCanvas
        ref="workflowRef"
        class="h-full"
        :default-model-settings="defaultModelSetting"
        :loop-workflow-mode="WorkflowMode.ApplicationLoop"
        :workflow-mode="WorkflowMode.Application"
      />
    </div>

    <!-- 发布内容 -->
    <EditPublishVersionDialog ref="publishDialogRef" mode="publish" :saving="loading" @submit="handlePublish" />
  </WorkflowViewLayout>
</template>
