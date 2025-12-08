<template>
  <div class="application-workflow" v-loading="loading">
    <div class="header border-b flex-between p-12-24 white-bg">
      <div class="flex align-center">
        <back-button @click="back"></back-button>
        <h4 class="ellipsis" style="max-width: 300px" :title="detail?.name">{{ detail?.name }}</h4>
        <div v-if="showHistory && disablePublic">
          <el-text type="info" class="ml-16 color-secondary"
            >{{ $t('views.applicationWorkflow.info.previewVersion') }}
            {{ currentVersion.name || datetimeFormat(currentVersion.update_time) }}</el-text
          >
        </div>
        <el-text type="info" class="ml-16 color-secondary" v-else-if="saveTime"
          >{{ $t('views.applicationWorkflow.info.saveTime')
          }}{{ datetimeFormat(saveTime) }}</el-text
        >
      </div>
      <div v-if="showHistory && disablePublic">
        <el-button type="primary" class="mr-8" @click="refreshVersion()">
          {{ $t('views.applicationWorkflow.setting.restoreVersion') }}
        </el-button>
        <el-divider direction="vertical" />
        <el-button text @click="closeHistory">
          <el-icon>
            <Close />
          </el-icon>
        </el-button>
      </div>
      <div v-else>
        <el-button @click="showPopover = !showPopover">
          <AppIcon iconName="app-add-outlined" class="mr-4" />
          {{ $t('views.applicationWorkflow.setting.addComponent') }}
        </el-button>
        <el-button @click="clickShowDebug" :disabled="showDebug" v-if="permissionPrecise.debug(id)">
          <AppIcon iconName="app-debug-outlined" class="mr-4"></AppIcon>
          {{ $t('views.applicationWorkflow.setting.debug') }}
        </el-button>
        <el-button @click="saveApplication(true)" v-if="permissionPrecise.edit(id)">
          <AppIcon iconName="app-save-outlined" class="mr-4"></AppIcon>
          {{ $t('common.save') }}
        </el-button>
        <el-button type="primary" @click="publish" v-if="permissionPrecise.edit(id)">
          {{ $t('views.application.operation.publish') }}
        </el-button>

        <el-dropdown trigger="click">
          <el-button text @click.stop class="ml-8 mt-4">
            <AppIcon iconName="app-more" class="rotate-90"></AppIcon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <a :href="shareUrl" target="_blank">
                <el-dropdown-item>
                  <AppIcon iconName="app-create-chat" class="color-secondary"></AppIcon>
                  {{ $t('views.application.operation.toChat') }}
                </el-dropdown-item>
              </a>

              <el-dropdown-item @click="openHistory">
                <AppIcon iconName="app-history-outlined" class="color-secondary"></AppIcon>
                {{ $t('views.applicationWorkflow.setting.releaseHistory') }}
              </el-dropdown-item>
              <el-dropdown-item>
                <AppIcon iconName="app-save-outlined" class="color-secondary"></AppIcon>
                {{ $t('views.applicationWorkflow.setting.autoSave') }}
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
                {{ detail?.name || $t('views.application.form.appName.label') }}
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
        <div class="scrollbar-height">
          <AiChat :application-details="detail" :type="'debug-ai-chat'"></AiChat>
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
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, nextTick, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Action } from 'element-plus'
import Workflow from '@/workflow/index.vue'
import DropdownMenu from '@/views/application-workflow/component/DropdownMenu.vue'
import PublishHistory from '@/views/application-workflow/component/PublishHistory.vue'
import { isAppIcon, resetUrl } from '@/utils/common'
import { MsgSuccess, MsgError, MsgConfirm } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import { mapToUrlParams } from '@/utils/application'
import useStore from '@/stores'
import { WorkFlowInstance } from '@/workflow/common/validate'
import { hasPermission } from '@/utils/permission'
import { t } from '@/locales'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
provide('getApplicationDetail', () => detail)
const { theme } = useStore()
const router = useRouter()
const route = useRoute()
const {
  params: { id, from },
} = route as any
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const permissionPrecise = computed(() => {
  return permissionMap['application'][apiType.value]
})

const isDefaultTheme = computed(() => {
  return theme.isDefaultTheme()
})

let interval: any
const workflowRef = ref()
const workflowMainRef = ref()
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

const urlParams = computed(() =>
  mapToUrlParams(apiInputParams.value) ? '?' + mapToUrlParams(apiInputParams.value) : '',
)
const shareUrl = computed(
  () => `${window.location.origin}/chat/` + detail.value?.access_token + urlParams.value,
)

function back() {
  if (JSON.stringify(cloneWorkFlow.value) !== JSON.stringify(getGraphData())) {
    MsgConfirm(t('common.tip'), t('views.applicationWorkflow.tip.saveMessage'), {
      confirmButtonText: t('views.applicationWorkflow.setting.exitSave'),
      cancelButtonText: t('views.applicationWorkflow.setting.exit'),
      distinguishCancelAndClose: true,
    })
      .then(() => {
        saveApplication(true, true)
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
  // if (hasPermission(`APPLICATION:MANAGE:${id}`, 'AND') && isSave.value) {
  //   initInterval()
  // }
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
      const workflowInstance = new WorkFlowInstance(workflow)
      try {
        workflowInstance.is_valid()
      } catch (e: any) {
        MsgError(e.toString())
        return
      }
      loadSharedApi({ type: 'application', systemType: apiType.value })
        .putApplication(id, { work_flow: workflow }, loading)
        .then(() => {
          return loadSharedApi({ type: 'application', systemType: apiType.value }).publish(
            id,
            {},
            loading,
          )
        })
        .then((ok: any) => {
          detail.value.name = ok.data.name
          ok.data.work_flow?.nodes
            ?.filter((v: any) => v.id === 'base-node')
            .map((v: any) => {
              apiInputParams.value = v.properties.api_input_field_list
                ? v.properties.api_input_field_list.map((v: any) => {
                    return {
                      name: v.variable,
                      value: v.default_value,
                    }
                  })
                : v.properties.input_field_list
                  ? v.properties.input_field_list
                      .filter((v: any) => v.assignment_method === 'api_input')
                      .map((v: any) => {
                        return {
                          name: v.variable,
                          value: v.default_value,
                        }
                      })
                  : []
            })
          MsgSuccess(t('views.application.tip.publishSuccess'))
        })
        .catch((res: any) => {
          const node = res.node
          const err_message = res.errMessage
          if (typeof err_message == 'string') {
            MsgError(
              res.node.properties?.stepName +
                ` ${t('views.applicationWorkflow.node').toLowerCase()} ` +
                err_message.toLowerCase(),
            )
          } else {
            const keys = Object.keys(err_message)
            MsgError(
              node.properties?.stepName +
                ` ${t('views.applicationWorkflow.node').toLowerCase()} ` +
                err_message[keys[0]]?.[0]?.message.toLowerCase(),
            )
          }
        })
    })
    .catch((res: any) => {
      const node = res.node
      const err_message = res.errMessage
      if (typeof err_message == 'string') {
        MsgError(
          res.node.properties?.stepName + ` ${t('views.applicationWorkflow.node')}，` + err_message,
        )
      } else {
        const keys = Object.keys(err_message)
        MsgError(
          node.properties?.stepName +
            ` ${t('views.applicationWorkflow.node')}，` +
            err_message[keys[0]]?.[0]?.message,
        )
      }
    })
}

const clickShowDebug = () => {
  workflowRef.value
    ?.validate()
    .then(() => {
      const graphData = getGraphData()
      const workflow = new WorkFlowInstance(graphData)
      try {
        workflow.is_valid()
        detail.value = {
          ...detail.value,
          type: 'WORK_FLOW',
          ...workflow.get_base_node()?.properties.node_data,
          work_flow: getGraphData(),
        }

        showDebug.value = true
      } catch (e: any) {
        MsgError(e.toString())
      }
    })
    .catch((res: any) => {
      const node = res.node
      const err_message = res.errMessage
      if (typeof err_message == 'string') {
        MsgError(
          res.node.properties?.stepName + ` ${t('views.applicationWorkflow.node')}，` + err_message,
        )
      } else {
        const keys = Object.keys(err_message)
        MsgError(
          node.properties?.stepName +
            ` ${t('views.applicationWorkflow.node')}，` +
            err_message[keys[0]]?.[0]?.message,
        )
      }
    })
}
function getGraphData() {
  return workflowRef.value?.getGraphData()
}

function getDetail() {
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getApplicationDetail(id)
    .then((res: any) => {
      res.data?.work_flow['nodes'].map((v: any) => {
        v['properties']['noRender'] = true
      })
      detail.value = res.data
      detail.value.stt_model_id = res.data.stt_model
      detail.value.tts_model_id = res.data.tts_model
      detail.value.tts_type = res.data.tts_type
      saveTime.value = res.data?.update_time
      detail.value.work_flow?.nodes
        ?.filter((v: any) => v.id === 'base-node')
        .map((v: any) => {
          apiInputParams.value = v.properties.api_input_field_list
            ? v.properties.api_input_field_list.map((v: any) => {
                return {
                  name: v.variable,
                  value: v.default_value,
                }
              })
            : v.properties.input_field_list
              ? v.properties.input_field_list
                  .filter((v: any) => v.assignment_method === 'api_input')
                  .map((v: any) => {
                    return {
                      name: v.variable,
                      value: v.default_value,
                    }
                  })
              : []
        })
      loadSharedApi({ type: 'application', systemType: apiType.value })
        .getAccessToken(id, loading)
        .then((res: any) => {
          detail.value = { ...detail.value, ...res.data }
        })
      workflowRef.value?.clearGraphData()
      nextTick(() => {
        workflowRef.value?.render(detail.value.work_flow)
        cloneWorkFlow.value = getGraphData()
      })
      // 企业版和专业版
      if (hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')) {
        loadSharedApi({ type: 'application', systemType: apiType.value })
          .getApplicationSetting(id)
          .then((ok: any) => {
            detail.value = { ...detail.value, ...ok.data }
          })
      }
    })
}

function saveApplication(bool?: boolean, back?: boolean) {
  const obj = {
    work_flow: getGraphData(),
  }
  loading.value = back || false
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .putApplication(id, obj)
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
  if (route.path.includes('workspace')) {
    return router.push({ path: get_route() })
  } else {
    return router.push({ path: get_resource_management_route() })
  }
}

const get_resource_management_route = () => {
  if (hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_APPLICATION_OVERVIEW_READ], 'OR')) {
    return `/application/${from}/${id}/WORK_FLOW/overview`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_APPLICATION_ACCESS_READ], 'OR')
  ) {
    return `/application/${from}/${id}/WORK_FLOW/access`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_APPLICATION_CHAT_USER_READ], 'OR')
  ) {
    return `/application/${from}/${id}/WORK_FLOW/chat-user`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_APPLICATION_CHAT_LOG_READ], 'OR')
  ) {
    return `/application/${from}/${id}/WORK_FLOW/chat-log`
  } else {
    return `/system/resource-management/application`
  }
}

const get_route = () => {
  if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(id)],
          [],
          'AND',
        ),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.APPLICATION_OVERVIEW_READ.getWorkspacePermissionWorkspaceManageRole,
        PermissionConst.APPLICATION_OVERVIEW_READ.getApplicationWorkspaceResourcePermission(id),
      ],
      'OR',
    )
  ) {
    return `/application/${from}/${id}/WORK_FLOW/overview`
  } else if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(id)],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'AND',
        ),
        new ComplexPermission(
          [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
          [PermissionConst.APPLICATION_ACCESS_READ.getWorkspacePermissionWorkspaceManageRole],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
        new ComplexPermission(
          [],
          [PermissionConst.APPLICATION_ACCESS_READ.getApplicationWorkspaceResourcePermission(id)],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
      ],
      'OR',
    )
  ) {
    return `/application/${from}/${id}/WORK_FLOW/access`
  } else if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(id)],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'AND',
        ),
        new ComplexPermission(
          [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
          [PermissionConst.APPLICATION_CHAT_USER_READ.getWorkspacePermissionWorkspaceManageRole],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
        new ComplexPermission(
          [],
          [
            PermissionConst.APPLICATION_CHAT_USER_READ.getApplicationWorkspaceResourcePermission(
              id,
            ),
          ],
          [EditionConst.IS_EE, EditionConst.IS_PE],
          'OR',
        ),
      ],
      'OR',
    )
  ) {
    return `/application/${from}/${id}/WORK_FLOW/chat-user`
  } else if (
    hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(id)],
          [],
          'AND',
        ),
        PermissionConst.APPLICATION_CHAT_LOG_READ.getWorkspacePermissionWorkspaceManageRole,
        PermissionConst.APPLICATION_CHAT_LOG_READ.getApplicationWorkspaceResourcePermission(id),
      ],
      'OR',
    )
  ) {
    return `/application/${from}/${id}/WORK_FLOW/chat-log`
  } else return `/application`
}

/**
 * 定时保存
 */
const initInterval = () => {
  interval = setInterval(() => {
    saveApplication()
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

onMounted(() => {
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
.application-workflow {
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
