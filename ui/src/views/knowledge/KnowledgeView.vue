<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedApi from '@/api/admin/workspace/shared'
import type { Dict, FolderItem, KnowledgeItem, OptionItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from '@/components/business/folder-tree/index.vue'
import KnowledgeCard from './components/KnowledgeCard.vue'

/* 当前文件夹 */
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.KNOWLEDGE].all })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder: FolderItem) {
  const folderChanged = folder.id !== currentFolder.value.id
  currentFolder.value = folder
  if (folderChanged) refreshKnowledge()
}

const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
function handleCreateFolder() {
  folderTreeRef.value?.openCreate()
}

/* 知识库查询 */
const knowledgeData = ref<KnowledgeItem[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const creatorOptions = ref<OptionItem<string>[]>([])
const searchFields = computed(() => [
  { label: '名称', value: 'name' },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const knowledgeQuery = ref<Dict<unknown>>()

function loadCreatorOptions(keyword: string) {
  const requestApi = isShared.value ? CommonSystemApi : CommonApi
  return requestApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: Dict<unknown>) {
  knowledgeQuery.value = query
  refreshKnowledge()
}

function loadKnowledgePage(pagination: { currentPage: number; pageSize: number }) {
  const request = isShared.value ? SharedApi : KnowledgeApi
  const folderId = isShared.value ? {} : { folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL }
  return request.getKnowledgePage(pagination, { ...knowledgeQuery.value, ...folderId })
}

/* 知识库维护 */
const knowledgeOperationLoading = ref(false)

function refreshKnowledge() {
  infiniteScrollRef.value?.reset()
}

function handleDeleteKnowledge(knowledgeId: string) {
  const knowledgeIndex = knowledgeData.value.findIndex((item) => item.id === knowledgeId)
  if (knowledgeIndex >= 0) knowledgeData.value.splice(knowledgeIndex, 1)
}
</script>

<template>
  <MkViewLayout class="workspace-knowledge-view" collapsible>
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <el-tooltip content="创建文件夹" placement="top">
          <el-button text type="primary" class="-mr-1" @click="handleCreateFolder">
            <MkIcon name="icon_add-folder_outlined" :size="18" />
          </el-button>
        </el-tooltip>
      </component>

      <FolderTree ref="folderTreeRef" :source="RESOURCE_TYPE.KNOWLEDGE" draggable @select="handleFolderSelect" />
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
        <div class="flex items-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />

          <MkDropdown v-if="!isShared" trigger="click" placement="bottom-end">
            <el-button type="primary">
              <span class="mr-1">创建</span>
              <MkIcon name="icon_down_outlined" :size="14" />
            </el-button>
            <template #dropdown>
              <MkDropdownMenu class="w-52!">
                <MkDropdownItem>通用知识库</MkDropdownItem>
                <MkDropdownItem>Web 站点知识库</MkDropdownItem>
                <MkDropdownItem>工作流知识库</MkDropdownItem>
                <MkDropdownItem divided>导入创建</MkDropdownItem>
              </MkDropdownMenu>
            </template>
          </MkDropdown>
        </div>
      </component>

      <div v-loading="knowledgeOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="knowledgeData" :load="loadKnowledgePage">
          <div v-if="knowledgeData.length" class="mk-resource-card-grid">
            <template v-for="knowledge in knowledgeData" :key="knowledge.id">
              <KnowledgeCard v-model:loading="knowledgeOperationLoading" :knowledge="knowledge" :shared="isShared" @delete="handleDeleteKnowledge" />
            </template>
          </div>
          <MkEmpty v-else class="mt-24" />
        </MkInfiniteScroll>
      </div>
    </template>
  </MkViewLayout>
</template>
