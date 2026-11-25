<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { ApplicationDetail, Dict, FolderItem, OptionItem } from '@/api/types'
import { APPLICATION_TYPE, RESOURCE_TYPE } from '@/api/enums'
import ApplicationApi from '@/api/admin/workspace/application/application'
import CommonApi from '@/api/admin/workspace/common'
import RelatedResourcesApi from '@/api/admin/workspace/related-resources'
import ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import FolderTree from '@/components/business/folder-tree/index.vue'
import ApplicationCard from './application-card/ApplicationCard.vue'
import {
  AuthorizeApplicationAction,
  CopyApplicationAction,
  DeleteApplicationAction,
  ExportApplicationAction,
  McpConfigApplicationAction,
  MoveApplicationAction,
  PortalApplicationAction,
  RelatedResourcesApplicationAction,
  SettingApplicationAction,
  TriggerApplicationAction,
} from './application-card/action-dropdown'
import ButtonBatchCleanStrategy from './components/ButtonBatchCleanStrategy.vue'
import ButtonCreateApplication from './components/ButtonCreateApplication.vue'
import ButtonTemplateStore from './components/ButtonTemplateStore.vue'
import { FOLDER_ENTRY_ID } from '@/constants/folder'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })

const route = useRoute()
const router = useRouter()

/* 当前文件夹 */
const currentFolderId = ref<string>(FOLDER_ENTRY_ID.ALL)
const selectedFolder = ref<FolderItem>()
const currentFolder = computed<FolderItem>(() => selectedFolder.value ?? { id: FOLDER_ENTRY_ID.ALL, name: t('application.categories.all') })

function handleFolderSelect(folder?: FolderItem) {
  const previousFolderId = currentFolder.value.id
  selectedFolder.value = folder
  currentFolderId.value = currentFolder.value.id
  if (previousFolderId !== currentFolderId.value) {
    cancelBatchSelection()
    refreshApplications()
  }
}

const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')

function handleCreateFolder() {
  folderTreeRef.value?.openCreate()
}

/* 智能体查询 */
const applicationData = ref<ApplicationDetail[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const creatorOptions = ref<OptionItem<string>[]>([])
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  {
    label: t('common.status.label'),
    value: 'status',
    options: [
      { label: t('application.status.unpublished'), value: 'unpublished' },
      { label: t('application.status.published'), value: 'published' },
      { label: t('application.status.onPortal'), value: 'on_portal' },
    ],
  },
  {
    label: t('common.labels.type'),
    value: 'type',
    options: [
      { label: t('application.simple.shortLabel'), value: APPLICATION_TYPE.SIMPLE },
      { label: t('application.advanced.shortLabel'), value: APPLICATION_TYPE.WORK_FLOW },
    ],
  },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const applicationQuery = ref<Dict<unknown>>()

function loadCreatorOptions(keyword: string) {
  return CommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: Dict<unknown>) {
  applicationQuery.value = query
  refreshApplications()
}

function loadApplicationPage(pagination: { currentPage: number; pageSize: number }) {
  return ApplicationApi.getApplicationPage(pagination, { ...applicationQuery.value, folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL })
}

/* 智能体维护 */
const applicationOperationLoading = ref(false)

function refreshApplications() {
  selectedApplicationIds.value = []
  return infiniteScrollRef.value?.reset()
}

function handleDeleteApplication(applicationId: string) {
  const applicationIndex = applicationData.value.findIndex(({ id }) => id === applicationId)
  if (applicationIndex >= 0) applicationData.value.splice(applicationIndex, 1)
}

/* card点击去详情 */
function handleToDetail(application: ApplicationDetail) {
  router.push({
    name: 'workspace-application-overview',
    params: { applicationId: application.id, type: application.type, workspaceId: route.params.workspaceId },
  })
}

/* 批量选择与操作 */
const batchSelectionMode = ref(false)
const selectedApplicationIds = ref<string[]>([])
const selectedApplicationCount = computed(() => selectedApplicationIds.value.length)
const applicationIds = computed(() => applicationData.value.map(({ id }) => id))
const batchMoveToDialogRef = useTemplateRef<{ close: () => void; open: (currentFolderId?: string) => void }>('batchMoveToDialogRef')

function toggleBatchSelection() {
  batchSelectionMode.value = !batchSelectionMode.value
  selectedApplicationIds.value = []
}

function cancelBatchSelection() {
  batchSelectionMode.value = false
  selectedApplicationIds.value = []
}

function handleBatchCleanStrategySuccess() {
  cancelBatchSelection()
  return refreshApplications()
}

function handleApplicationSelect(applicationId: string, selected: boolean) {
  if (selected) {
    if (!selectedApplicationIds.value.includes(applicationId)) selectedApplicationIds.value.push(applicationId)
    return
  }

  selectedApplicationIds.value = selectedApplicationIds.value.filter((id) => id !== applicationId)
}

function handleOpenBatchMove() {
  if (!selectedApplicationCount.value) return
  batchMoveToDialogRef.value?.open(currentFolder.value.id)
}

// 批量移动
function handleBatchMove(targetFolderId: string) {
  if (applicationOperationLoading.value || !selectedApplicationCount.value) return
  const applicationIds = [...selectedApplicationIds.value]

  applicationOperationLoading.value = true
  return ApplicationApi.putBatchMoveApplications(applicationIds, targetFolderId)
    .then(() => {
      MsgSuccess(t('common.messages.moveSuccess'))
      batchMoveToDialogRef.value?.close()
      cancelBatchSelection()
      return refreshApplications()
    })
    .finally(() => {
      applicationOperationLoading.value = false
    })
}

// 批量操作
function handleBatchDelete() {
  if (!selectedApplicationCount.value) return
  const applicationIds = [...selectedApplicationIds.value]

  MsgConfirm(t('application.delete.batchTitle', { count: applicationIds.length }, applicationIds.length), t('common.dialogs.deleteWarning'))
    .then(() => {
      applicationOperationLoading.value = true
      return ApplicationApi.putBatchDeleteApplications(applicationIds).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
        cancelBatchSelection()
        return refreshApplications()
      })
    })
    .catch(() => {})
    .finally(() => {
      applicationOperationLoading.value = false
    })
}
</script>

<template>
  <MkViewLayout :title="t('application.title')" class="workspace-application-view" collapsible resizable>
    <template v-if="perm.application.workspace.folderReadWorkspace()" #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkTooltip v-if="perm.application.workspace.folderCreateWorkspace()" :content="t('folder.actions.create')" placement="top">
          <el-button @click="handleCreateFolder" text type="primary" class="-mr-1">
            <MkIcon name="icon_add-folder_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>

      <FolderTree
        ref="folderTreeRef"
        v-model="currentFolderId"
        :source="RESOURCE_TYPE.APPLICATION"
        :show-shared="false"
        draggable
        @loaded="handleFolderSelect"
        @select="handleFolderSelect"
      />
    </template>

    <template #default="{ Footer, Header }">
      <component :is="Header">
        <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 批量选择 -->
          <span
            v-if="
              perm.application.workspace.batchMove() || perm.application.workspace.batchCleanStrategy() || perm.application.workspace.batchDelete()
            "
          >
            <el-button :disabled="!applicationData.length" :type="batchSelectionMode ? 'primary' : undefined" plain @click="toggleBatchSelection">
              <MkIcon name="icon_Batch_outlined" />
              <span>{{ t(batchSelectionMode ? 'common.actions.cancelSelection' : 'common.actions.batchSelect') }}</span>
            </el-button>
          </span>

          <template v-if="!batchSelectionMode">
            <!-- 模板中心 -->
            <ButtonTemplateStore v-if="perm.application.workspace.create()" :folder-id="currentFolder.id" />
            <!-- 创建智能体 -->
            <ButtonCreateApplication v-if="perm.application.workspace.create()" :folder-id="currentFolder.id" @refresh="refreshApplications" />
          </template>
        </div>
      </component>

      <div v-loading="applicationOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="applicationData" :load="loadApplicationPage">
          <div class="mk-resource-card-grid">
            <template v-for="application in applicationData" :key="application.id">
              <ApplicationCard
                :application="application"
                :selectable="batchSelectionMode"
                :selected="selectedApplicationIds.includes(application.id)"
                @click="handleToDetail(application)"
                @selected="handleApplicationSelect(application.id, $event)"
              >
                <template #action-dropdown>
                  <!-- 设置 -->
                  <SettingApplicationAction
                    v-if="perm.application.workspace.edit(application.id)"
                    :label="t('common.labels.settings')"
                    :application="application"
                  />
                  <!-- 智能体触发器 -->
                  <TriggerApplicationAction
                    v-if="perm.application.workspace.triggerRead(application.id)"
                    :label="t('trigger.title')"
                    :api="ResourceTriggerApi"
                    :application-api="ApplicationApi"
                    :application="application"
                  />
                  <!-- MCP 服务配置 -->
                  <McpConfigApplicationAction
                    v-if="perm.application.workspace.mcpConfig(application.id)"
                    :label="t('resource.mcpConfig.title')"
                    :application="application"
                  />
                  <!-- 资源授权 -->
                  <AuthorizeApplicationAction
                    v-if="perm.application.workspace.auth(application.id)"
                    :label="t('authorization.resource.title')"
                    :application="application"
                  />
                  <!-- 查看关联资源 -->
                  <RelatedResourcesApplicationAction
                    v-if="perm.application.workspace.relateMap(application.id)"
                    :label="t('resource.relations.title')"
                    :api="RelatedResourcesApi"
                    :application="application"
                  />
                  <!-- 复制 -->
                  <CopyApplicationAction
                    v-model:loading="applicationOperationLoading"
                    :label="t('common.actions.copy')"
                    :api="ApplicationApi"
                    :application="application"
                    :folder-id="currentFolder.id"
                    @refresh="refreshApplications"
                    v-if="perm.application.workspace.copy(application.id)"
                  />
                  <!-- 移动到 -->
                  <MoveApplicationAction
                    v-if="perm.application.workspace.move(application.id)"
                    v-model:loading="applicationOperationLoading"
                    :label="t('folder.actions.moveTo')"
                    :api="ApplicationApi"
                    :application="application"
                    :current-folder-id="currentFolder.id"
                    @delete="handleDeleteApplication"
                  />
                  <!-- 门户上下架 -->
                  <PortalApplicationAction
                    v-model:loading="applicationOperationLoading"
                    :api="ApplicationApi"
                    :application="application"
                    @change="application.is_portal = $event"
                    v-if="(!application.is_portal && perm.application.workspace.portalUp(application.id) && application.is_publish) || (application.is_portal && perm.application.workspace.portalDown(application.id))"
                  />
                  <!-- 导出 -->
                  <ExportApplicationAction
                    v-model:loading="applicationOperationLoading"
                    :label="t('common.actions.export')"
                    :api="ApplicationApi"
                    :application="application"
                    v-if="perm.application.workspace.export(application.id) || perm.application.workspace.exportSkills(application.id)"
                  />
                  <!-- 删除 -->
                  <DeleteApplicationAction
                    v-model:loading="applicationOperationLoading"
                    :label="t('common.actions.delete')"
                    :api="ApplicationApi"
                    :application="application"
                    @delete="handleDeleteApplication"
                    v-if="perm.application.workspace.delete(application.id)"
                  />
                </template>
              </ApplicationCard>
            </template>
          </div>
          <template #empty>
            <MkEmpty class="mt-24" />
          </template>
        </MkInfiniteScroll>
      </div>

      <component
        :is="Footer"
        v-if="batchSelectionMode"
        v-model:batch-selection="selectedApplicationIds"
        :batch-values="applicationIds"
        @batch-cancel="cancelBatchSelection"
      >
        <template #footer-batch-actions>
          <el-button
            v-if="perm.application.workspace.batchMove()"
            type="primary"
            plain
            :disabled="!selectedApplicationCount"
            @click="handleOpenBatchMove"
          >
            {{ t('folder.actions.moveTo') }}
          </el-button>
          <!-- 批量设置清除策略 -->
          <ButtonBatchCleanStrategy
            v-if="perm.application.workspace.batchCleanStrategy()"
            :application-ids="selectedApplicationIds"
            @refresh="handleBatchCleanStrategySuccess"
          />
          <el-button
            v-if="perm.application.workspace.batchDelete()"
            type="danger"
            plain
            :disabled="!selectedApplicationCount"
            @click="handleBatchDelete"
          >
            {{ t('common.actions.delete') }}
          </el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>

  <MoveToDialog ref="batchMoveToDialogRef" :loading="applicationOperationLoading" :source="RESOURCE_TYPE.APPLICATION" @submit="handleBatchMove" />
</template>
