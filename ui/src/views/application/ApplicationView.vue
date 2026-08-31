<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommonApi from '@/api/admin/workspace/common'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail, Dict, FolderItem, OptionItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from '@/components/business/folder-tree/index.vue'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ApplicationCard from './application-card/ApplicationCard.vue'
import { DeleteApplicationAction, ExportApplicationAction, MoveApplicationAction, SettingApplicationAction } from './application-card/action-dropdown'
import CreateApplicationDropdown from './create-application/CreateApplicationDropdown.vue'

const route = useRoute()
const router = useRouter()

/* 当前文件夹 */
const allApplicationsFolder = FOLDER_ENTRIES[RESOURCE_TYPE.APPLICATION].all
const routeFolderId = typeof route.query.folderId === 'string' && route.query.folderId ? route.query.folderId : FOLDER_ENTRY_ID.ALL
const currentFolderId = ref(routeFolderId)
const currentFolder = ref<FolderItem>({ ...allApplicationsFolder, id: currentFolderId.value })

function syncFolderQuery(folderId: string) {
  const folderIdQuery = folderId === FOLDER_ENTRY_ID.ALL ? undefined : folderId
  if (route.query.folderId === folderIdQuery) return

  void router.replace({ query: { ...route.query, folderId: folderIdQuery } })
}

function handleFolderSelect(folder: FolderItem) {
  const folderChanged = folder.id !== currentFolder.value.id
  currentFolderId.value = folder.id
  currentFolder.value = folder
  syncFolderQuery(folder.id)
  if (folderChanged) {
    cancelBatchSelection()
    refreshApplications()
  }
}

function handleFolderLoaded(folder?: FolderItem) {
  handleFolderSelect(folder ?? allApplicationsFolder)
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
  { label: '名称', value: 'name' },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
  {
    label: '发布状态',
    value: 'publish_status',
    options: [
      { label: '已发布', value: 'published' },
      { label: '未发布', value: 'unpublished' },
    ],
  },
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

function handleOpenApplication(application: ApplicationDetail) {
  void router.push({
    name: 'workspace-application-detail',
    params: { applicationId: application.id, type: application.type, workspaceId: route.params.workspaceId },
    query: route.query,
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
      MsgSuccess('移动成功')
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

  MsgConfirm(`是否批量删除 ${applicationIds.length} 个智能体？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      applicationOperationLoading.value = true
      return ApplicationApi.putBatchDeleteApplications(applicationIds).then(() => {
        MsgSuccess('删除成功')
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
  <MkViewLayout class="workspace-application-view" collapsible>
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <el-tooltip content="创建文件夹" placement="top">
          <el-button @click="handleCreateFolder" text type="primary" class="-mr-1">
            <MkIcon name="icon_add-folder_outlined" :size="18" />
          </el-button>
        </el-tooltip>
      </component>

      <FolderTree
        ref="folderTreeRef"
        v-model="currentFolderId"
        :source="RESOURCE_TYPE.APPLICATION"
        :show-shared="false"
        draggable
        @loaded="handleFolderLoaded"
        @select="handleFolderSelect"
      />
    </template>

    <template #default="{ Footer, Header }">
      <component :is="Header">
        <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
        <div class="flex items-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <el-button v-if="applicationData.length" :type="batchSelectionMode ? 'primary' : undefined" plain @click="toggleBatchSelection">
            <MkIcon name="icon_Batch_outlined" />
            <span>{{ batchSelectionMode ? '取消选择' : '批量选择' }}</span>
          </el-button>

          <CreateApplicationDropdown v-if="!batchSelectionMode" :folder-id="currentFolder.id" @refresh="refreshApplications" />
        </div>
      </component>

      <div v-loading="applicationOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="applicationData" :load="loadApplicationPage">
          <div v-if="applicationData.length" class="mk-resource-card-grid">
            <template v-for="application in applicationData" :key="application.id">
              <ApplicationCard
                :application="application"
                :selectable="batchSelectionMode"
                :selected="selectedApplicationIds.includes(application.id)"
                @open="handleOpenApplication(application)"
                @selected="handleApplicationSelect(application.id, $event)"
              >
                <template #action-dropdown>
                  <SettingApplicationAction label="设置" :application="application" />
                  <MoveApplicationAction
                    v-model:loading="applicationOperationLoading"
                    label="移动到"
                    :api="ApplicationApi"
                    :application="application"
                    :current-folder-id="currentFolder.id"
                    @delete="handleDeleteApplication"
                  />
                  <ExportApplicationAction
                    v-model:loading="applicationOperationLoading"
                    label="导出"
                    :api="ApplicationApi"
                    :application="application"
                  />
                  <DeleteApplicationAction
                    v-model:loading="applicationOperationLoading"
                    label="删除"
                    :api="ApplicationApi"
                    :application="application"
                    @delete="handleDeleteApplication"
                  />
                </template>
              </ApplicationCard>
            </template>
          </div>
          <MkEmpty v-else class="mt-24" />
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
          <el-button type="primary" plain :disabled="!selectedApplicationCount" @click="handleOpenBatchMove">移动到</el-button>
          <el-button type="danger" plain :disabled="!selectedApplicationCount" @click="handleBatchDelete">删除</el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>

  <MoveToDialog ref="batchMoveToDialogRef" :loading="applicationOperationLoading" :source="RESOURCE_TYPE.APPLICATION" @submit="handleBatchMove" />
</template>
