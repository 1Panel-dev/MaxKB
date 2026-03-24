<template>
  <div class="knowledge-workflow" v-loading="loading">
    <div class="header border-b flex-between p-12-24 white-bg">
      <div class="flex align-center">
        <back-button @click="back"></back-button>
        <h4 class="ellipsis" style="max-width: 300px" :title="detail?.name">{{ detail?.name }}</h4>
        <div v-if="showHistory && disablePublic">
          <el-text type="info" class="ml-16 color-secondary"
            >{{ $t('workflow.info.previewVersion') }}
            {{ currentVersion.name || datetimeFormat(currentVersion.update_time) }}
          </el-text>
        </div>
        <el-text type="info" class="ml-16 color-secondary" v-else-if="saveTime"
          >{{ $t('workflow.info.saveTime') }}{{ datetimeFormat(saveTime) }}
        </el-text>
      </div>
      <div v-if="showHistory && disablePublic && !route.path.includes('share/')">
        <el-button type="primary" class="mr-8" @click="refreshVersion()">
          {{ $t('workflow.setting.restoreVersion') }}
        </el-button>
        <el-divider direction="vertical" />
        <el-button text @click="closeHistory">
          <el-icon>
            <Close />
          </el-icon>
        </el-button>
      </div>
      <div v-else-if="!route.path.includes('share/')">
        <el-button
          class="ml-8"
          v-if="permissionPrecise.create()"
          @click="openTemplateStoreDialog()"
        >
          <AppIcon iconName="app-template-center" class="mr-4" />
          {{ $t('workflow.setting.templateCenter') }}
        </el-button>
        <el-button @click="showPopover = !showPopover">
          <AppIcon iconName="app-add-outlined" class="mr-4" />
          {{ $t('workflow.setting.addComponent') }}
        </el-button>
        <el-button @click="clickShowDebug" :disabled="showDebug" v-if="permissionPrecise.debug(id)">
          <AppIcon iconName="app-debug-outlined" class="mr-4"></AppIcon>
          {{ $t('common.debug') }}
        </el-button>
        <el-button v-if="permissionPrecise.workflow_edit(id)" @click="saveTool(true)">
          <AppIcon iconName="app-save-outlined" class="mr-4"></AppIcon>
          {{ $t('common.save') }}
        </el-button>
        <el-button type="primary" v-if="permissionPrecise.workflow_edit(id)" @click="publish">
          {{ $t('common.publish') }}
        </el-button>

        <el-dropdown trigger="click">
          <el-button text @click.stop class="ml-8 mt-4">
            <AppIcon iconName="app-more" class="rotate-90"></AppIcon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                @click.stop="exportToolWorkflow(detail.name, detail.id)"
                v-if="permissionPrecise.workflow_export(id)"
              >
                <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                {{ $t('workflow.operation.exportWorkflow') }}
              </el-dropdown-item>

              <el-dropdown-item @click="openHistory">
                <AppIcon iconName="app-history-outlined" class="color-secondary"></AppIcon>
                {{ $t('workflow.setting.releaseHistory') }}
              </el-dropdown-item>
              <el-dropdown-item v-if="permissionPrecise.workflow_edit(id)">
                <AppIcon iconName="app-save-outlined" class="color-secondary"></AppIcon>
                {{ $t('workflow.setting.autoSave') }}
                <div class="ml-4">
                  <el-switch size="small" v-model="isSave" @change="changeSave" />
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <!-- 下拉框 -->
    <el-collapse-transition>
      <DropdownMenu
        :show="showPopover"
        :id="id"
        v-click-outside="clickoutside"
        @clickNodes="clickNodes"
        @onmousedown="onmousedown"
        :workflowRef="workflowRef"
      />
    </el-collapse-transition>
    <!-- 主画布 -->
    <div class="workflow-main" ref="workflowMainRef">
      <workflow ref="workflowRef" v-if="detail" :data="detail?.work_flow" />
    </div>
    <!-- 调试 -->
    <el-collapse-transition>
      <div class="workflow-debug-container" :class="enlarge ? 'enlarge' : ''" v-if="showDebug">
        <div class="workflow-debug-header" :class="!isDefaultTheme ? 'custom-header' : ''">
          <div class="flex-between">
            <div class="flex align-center">
              <div class="mr-12 ml-24 flex">
                <el-avatar
                  v-if="isAppIcon(detail?.icon)"
                  shape="square"
                  :size="32"
                  style="background: none"
                >
                  <img :src="resetUrl(detail?.icon)" alt="" />
                </el-avatar>
                <LogoIcon v-else height="32px" />
              </div>

              <h4 class="ellipsis" style="max-width: 270px" :title="detail?.name">
                {{ detail?.name || $t('views.knowledge.form.appName.label') }}
              </h4>
            </div>
            <div class="mr-16">
              <el-button link @click="enlarge = !enlarge">
                <AppIcon
                  :iconName="enlarge ? 'app-minify' : 'app-magnify'"
                  class="color-secondary"
                  style="font-size: 20px"
                >
                </AppIcon>
              </el-button>
              <el-button link @click="showDebug = false">
                <el-icon :size="20" class="color-secondary">
                  <Close />
                </el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-collapse-transition>

    <!-- 发布历史 -->
    <PublishHistory
      v-if="showHistory"
      @click="checkVersion"
      v-click-outside="clickoutsideHistory"
      @refreshVersion="refreshVersion"
    />
    <TemplateStoreDialog
      ref="templateStoreDialogRef"
      :api-type="apiType"
      source="work_flow"
      @refresh="getDetail"
    />
    <DebugDrawer ref="debugDrawerRef"></DebugDrawer>
  </div>
</template>
<script setup lang="ts">
import { ref, onBeforeMount, onBeforeUnmount, computed, nextTick, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Action } from 'element-plus'
import Workflow from '@/workflow/index.vue'
import DropdownMenu from '@/components/workflow-dropdown-menu/index.vue'

import PublishHistory from '@/views/tool-workflow/component/PublishHistory.vue'
import { isAppIcon, resetUrl } from '@/utils/common'
import { MsgSuccess, MsgError, MsgConfirm } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import useStore from '@/stores'
import { ToolWorkFlowInstance } from '@/workflow/common/validate'
import { hasPermission } from '@/utils/permission'
import { t } from '@/locales'
import { ComplexPermission, Permission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import permissionMap from '@/permission'
import { WorkflowMode } from '@/enums/application'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { toolBaseNode, toolStartNode } from '@/workflow/common/data'
import TemplateStoreDialog from '@/views/knowledge/template-store/TemplateStoreDialog.vue'
import DebugDrawer from './debug-drawer/DebugDrawer.vue'
provide('getResourceDetail', () => detail)
provide('workflowMode', WorkflowMode.Tool)
provide('loopWorkflowMode', WorkflowMode.ToolLoop)
const { theme } = useStore()
const router = useRouter()
const route = useRoute()
const {
  params: { id, folderId },
  /*
  folderId 可以区分 resource-management shared还是 workspace
  */
} = route as any
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('share/')) {
    return 'workspaceShare'
  } else {
    return 'workspace'
  }
})

const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const isDefaultTheme = computed(() => {
  return theme.isDefaultTheme()
})

const workflowRef = ref()
const debugDrawerRef = ref<InstanceType<typeof DebugDrawer>>()
const loading = ref(false)
const detail = ref<any>(null)

const showPopover = ref(false)
const showDebug = ref(false)
const enlarge = ref(false)
const saveTime = ref<any>('')
const isSave = ref(false)
const showHistory = ref(false)
const disablePublic = ref(false)
const currentVersion = ref<any>({})
const cloneWorkFlow = ref(null)

const apiInputParams = ref([])

const isPublish = computed(() => detail.value?.is_publish)

function back() {
  if (JSON.stringify(cloneWorkFlow.value) !== JSON.stringify(getGraphData())) {
    MsgConfirm(t('common.tip'), t('workflow.tip.saveMessage'), {
      confirmButtonText: t('workflow.setting.exitSave'),
      cancelButtonText: t('workflow.setting.exit'),
      distinguishCancelAndClose: true,
    })
      .then(() => {
        saveTool(true, true)
      })
      .catch((action: Action) => {
        if (action === 'cancel') {
          go()
        }
      })
  } else {
    go()
  }
}

function clickoutsideHistory() {
  if (!disablePublic.value) {
    showHistory.value = false
    disablePublic.value = false
  }
}

function refreshVersion(item?: any) {
  if (item) {
    renderGraphData(item)
  }
  showHistory.value = false
  disablePublic.value = false
}

function checkVersion(item: any) {
  disablePublic.value = true
  currentVersion.value = item
  renderGraphData(item)
  closeInterval()
}

function renderGraphData(item: any) {
  item.work_flow['nodes'].map((v: any) => {
    v['properties']['noRender'] = true
  })
  detail.value.work_flow = item.work_flow
  saveTime.value = item?.update_time
  workflowRef.value?.clearGraphData()
  nextTick(() => {
    workflowRef.value?.render(item.work_flow)
  })
}

function closeHistory() {
  getDetail()
  if (isSave.value) {
    initInterval()
  }
  showHistory.value = false
  disablePublic.value = false
}

function openHistory() {
  showHistory.value = true
}

function changeSave(bool: boolean) {
  if (bool) {
    initInterval()
  } else {
    closeInterval()
  }
  localStorage.setItem('workflowAutoSave', bool.toString())
}

function clickNodes(item: any) {
  showPopover.value = false
}

function onmousedown(item: any) {
  showPopover.value = false
}

function clickoutside() {
  showPopover.value = false
}

const publish = () => {
  workflowRef.value
    ?.validate()
    .then(() => {
      const workflow = getGraphData()
      const workflowInstance = new ToolWorkFlowInstance(workflow, WorkflowMode.Tool)
      try {
        workflowInstance.is_valid()
      } catch (e: any) {
        console.log('ss', workflow)
        MsgError(e.toString())
        return
      }
      loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
        .putToolWorkflow(id, { work_flow: workflow })
        .then(() => {
          return loadSharedApi({
            type: 'tool',
            isShared: isShared.value,
            systemType: apiType.value,
          }).publish(id, {}, loading)
        })
        .then((ok: any) => {
          detail.value.is_publish = true
          MsgSuccess(t('views.application.tip.publishSuccess'))
        })
        .catch((res: any) => {
          console.log(res)
          const node = res.node
          const err_message = res.errMessage
          if (typeof err_message == 'string') {
            MsgError(
              res.node.properties?.stepName +
                ` ${t('workflow.node').toLowerCase()} ` +
                err_message.toLowerCase(),
            )
          } else {
            const keys = Object.keys(err_message)
            MsgError(
              node.properties?.stepName +
                ` ${t('workflow.node').toLowerCase()} ` +
                err_message[keys[0]]?.[0]?.message.toLowerCase(),
            )
          }
        })
    })
    .catch((res: any) => {
      const node = res.node
      const err_message = res.errMessage
      if (typeof err_message == 'string') {
        MsgError(res.node.properties?.stepName + ` ${t('workflow.node')}，` + err_message)
      } else {
        const keys = Object.keys(err_message)
        MsgError(
          node.properties?.stepName +
            ` ${t('workflow.node')}，` +
            err_message[keys[0]]?.[0]?.message,
        )
      }
    })
}

const elUploadRef = ref()
const importKnowledgeWorkflow = (file: any) => {
  const formData = new FormData()
  formData.append('file', file.raw)
  const name = file.name.replace('.kbwf', '')
  elUploadRef.value.clearFiles()
  MsgConfirm(
    t('common.tip'),
    `${t('views.application.tip.confirmUse')} ${name} ${t('views.application.tip.overwrite')}?`,
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
    },
  )
    .then(() => {
      loadSharedApi({ type: 'knowledge', isShared: isShared.value, systemType: apiType.value })
        .importKnowledgeWorkflow(id, formData, loading)
        .then(() => {
          getDetail()
        })
        .catch((error: any) => {
          if (error.code === 400) {
            MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
              cancelButtonText: t('common.confirm'),
              confirmButtonText: t('common.professional'),
            }).then(() => {
              window.open('https://maxkb.cn/pricing.html', '_blank')
            })
          }
        })
    })
    .catch(() => {})
}

function exportToolWorkflow(name: string, id: string) {
  loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .exportToolWorkflow(id, name, loading)
    .catch((error: any) => {
      if (error.response.status !== 403) {
        error.response.data.text().then((res: string) => {
          MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
        })
      }
    })
}

const clickShowDebug = () => {
  workflowRef.value
    ?.validate()
    .then(() => {
      const graphData = getGraphData()
      const workflow = new ToolWorkFlowInstance(graphData, WorkflowMode.Tool)
      try {
        workflow.is_valid()
        detail.value = {
          ...detail.value,
          type: 'WORK_FLOW',
          ...workflow.get_base_node()?.properties.node_data,
          work_flow: getGraphData(),
        }
        debugDrawerRef.value?.open(id)
      } catch (e: any) {
        MsgError(e.toString())
      }
    })
    .catch((res: any) => {
      const node = res.node
      const err_message = res.errMessage
      if (typeof err_message == 'string') {
        MsgError(res.node.properties?.stepName + ` ${t('workflow.node')}，` + err_message)
      } else {
        const keys = Object.keys(err_message)
        MsgError(
          node.properties?.stepName +
            ` ${t('workflow.node')}，` +
            err_message[keys[0]]?.[0]?.message,
        )
      }
    })
}

function getGraphData() {
  return workflowRef.value?.getGraphData()
}

const isShared = computed(() => {
  return folderId === 'share'
})

function getDetail() {
  loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .getToolById(id)
    .then((res: any) => {
      detail.value = res.data
      saveTime.value = res.data?.update_time
      console.log(res.data)
      if (!detail.value.work_flow || !('nodes' in detail.value.work_flow)) {
        detail.value.work_flow = { nodes: [toolBaseNode, toolStartNode] }
      }

      workflowRef.value?.clearGraphData()
      nextTick(() => {
        workflowRef.value?.render(detail.value.work_flow)
        cloneWorkFlow.value = getGraphData()
      })
    })
}

function saveTool(bool?: boolean, back?: boolean) {
  const obj = {
    work_flow: getGraphData(),
  }
  loading.value = back || false
  loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .putToolWorkflow(id, obj)
    .then(() => {
      saveTime.value = new Date()
      if (bool) {
        cloneWorkFlow.value = getGraphData()
        MsgSuccess(t('common.saveSuccess'))
        if (back) {
          go()
        }
      }
    })
    .catch(() => {
      loading.value = false
    })
}

const go = () => {
  if (route.path.includes('resource-management')) {
    return router.push({ path: '/system/resource-management/tool' })
  } else if (route.path.includes('shared')) {
    return router.push({ path: '/system/shared/tool' })
  } else {
    return router.push({ path: '/tool' })
  }
}

const templateStoreDialogRef = ref()
function openTemplateStoreDialog() {
  templateStoreDialogRef.value?.open(folderId)
}
let interval: any
/**
 * 定时保存
 */
const initInterval = () => {
  interval = setInterval(() => {
    saveTool()
  }, 60000)
}

/**
 * 关闭定时
 */
const closeInterval = () => {
  if (interval) {
    clearInterval(interval)
  }
}

onBeforeMount(() => {
  getDetail()
  const workflowAutoSave = localStorage.getItem('workflowAutoSave')
  isSave.value = workflowAutoSave === 'true' ? true : false
  // 初始化定时任务
  if (isSave.value) {
    initInterval()
  }
})

onBeforeUnmount(() => {
  // 清除定时任务
  closeInterval()
  workflowRef.value?.clearGraphData()
})
</script>
<style lang="scss">
.knowledge-workflow {
  background: var(--app-layout-bg-color);
  height: 100%;

  .workflow-main {
    height: calc(100vh - 62px);
    box-sizing: border-box;
  }

  .workflow-dropdown-tabs {
    .el-tabs__nav-wrap {
      padding: 0 16px;
    }
  }
}

.workflow-debug-container {
  z-index: 2000;
  position: relative;
  border-radius: 8px;
  border: 1px solid #ffffff;
  background: var(--dialog-bg-gradient-color);
  box-shadow: 0px 4px 8px 0px var(--app-text-color-light-1);
  position: fixed;
  bottom: 16px;
  right: 16px;
  overflow: hidden;
  width: 460px;
  height: 680px;

  .workflow-debug-header {
    background: var(--app-header-bg-color);
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-border-color);
  }

  .scrollbar-height {
    height: calc(100% - var(--app-header-height) - 24px);
    padding-top: 24px;
  }

  &.enlarge {
    width: 50% !important;
    height: 100% !important;
    bottom: 0 !important;
    right: 0 !important;
  }

  .chat-width {
    max-width: 100% !important;
    margin: 0 auto;
  }
}

@media only screen and (max-height: 680px) {
  .workflow-debug-container {
    height: 600px;
  }
}
</style>
