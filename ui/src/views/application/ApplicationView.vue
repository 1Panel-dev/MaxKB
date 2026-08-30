<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import CommonApi from '@/api/admin/workspace/common'
import ApplicationApi from '@/api/admin/workspace/application/application.ts'
import type { ApplicationDetail, Dict, FolderItem, OptionItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from '@/components/business/folder-tree/index.vue'
import ApplicationCard from './components/ApplicationCard.vue'
import ApplicationCreateDropdown from './components/ApplicationCreateDropdown.vue'

/* 当前文件夹 */
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.APPLICATION].all })

function handleFolderSelect(folder: FolderItem) {
  const folderChanged = folder.id !== currentFolder.value.id
  currentFolder.value = folder
  if (folderChanged) infiniteScrollRef.value?.reset()
}
// 新建文件夹
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
  infiniteScrollRef.value?.reset()
}

function handleRefreshApplications() {
  infiniteScrollRef.value?.reset()
}

function loadApplicationPage(pagination: { currentPage: number; pageSize: number }) {
  return ApplicationApi.getApplicationPage(pagination, { ...applicationQuery.value, folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL })
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

      <FolderTree ref="folderTreeRef" :source="RESOURCE_TYPE.APPLICATION" @select="handleFolderSelect" :show-shared="false" draggable> </FolderTree>
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
        <div class="flex items-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />

          <ApplicationCreateDropdown :folder-id="currentFolder.id" @refresh="handleRefreshApplications" />
        </div>
      </component>

      <MkInfiniteScroll ref="infiniteScrollRef" v-model="applicationData" :load="loadApplicationPage">
        <div v-if="applicationData.length" class="mk-resource-card-grid">
          <template v-for="application in applicationData" :key="application.id">
            <ApplicationCard :application="application" />
          </template>
        </div>
        <MkEmpty v-else class="mt-24" />
      </MkInfiniteScroll>
    </template>
  </MkViewLayout>
</template>
