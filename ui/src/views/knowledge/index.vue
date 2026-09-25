<script setup lang="ts">
import RelatedResourcesApi from '@/api/admin/workspace/related-resources'
import { computed, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedKnowledgeApi from '@/api/admin/workspace/shared/knowledge/knowledge.ts'
import type { Dict, FolderItem, KnowledgeItem, OptionItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from '@/components/business/folder-tree/index.vue'
import KnowledgeCard from './knowledge-card/KnowledgeCard.vue'
import ButtonCreateKnowledge from './components/ButtonCreateKnowledge.vue'
import ButtonTemplateStore from './components/ButtonTemplateStore.vue'
import {
  AuthorizeKnowledgeAction,
  DeleteKnowledgeAction,
  ExportKnowledgeAction,
  KeywordIndexKnowledgeAction,
  McpConfigKnowledgeAction,
  MoveKnowledgeAction,
  RelatedResourcesKnowledgeAction,
  SettingKnowledgeAction,
} from './knowledge-card/action-dropdown'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

/* 知识库详情入口 */
const route = useRoute()
const router = useRouter()

function handleOpenKnowledge(knowledge: KnowledgeItem) {
  void router.push({
    name: isShared.value ? 'workspace-shared-knowledge-detail' : 'workspace-knowledge-detail',
    params: { workspaceId: route.params.workspaceId, knowledgeId: knowledge.id },
  })
}

/* 当前文件夹 */
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.KNOWLEDGE].all })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder: FolderItem) {
  const folderChanged = folder.id !== currentFolder.value.id
  currentFolder.value = folder
  if (folderChanged) {
    cancelBatchSelection()
    refreshKnowledge()
  }
}

const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
function handleCreateFolder() {
  folderTreeRef.value?.openCreate()
}

/* 创建知识库 */
const createFolderId = computed(() => currentFolder.value.id || FOLDER_ENTRY_ID.ALL)

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
  const requestApi = isShared.value ? SharedKnowledgeApi : KnowledgeApi
  const folderId = isShared.value ? {} : { folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL }
  return requestApi.getKnowledgePage(pagination, { ...knowledgeQuery.value, ...folderId })
}

/* 知识库维护 */
const knowledgeOperationLoading = ref(false)

function refreshKnowledge() {
  selectedKnowledgeIds.value = []
  return infiniteScrollRef.value?.reset()
}

function handleDeleteKnowledge(knowledgeId: string) {
  const knowledgeIndex = knowledgeData.value.findIndex((item) => item.id === knowledgeId)
  if (knowledgeIndex >= 0) knowledgeData.value.splice(knowledgeIndex, 1)
  selectedKnowledgeIds.value = selectedKnowledgeIds.value.filter((id) => id !== knowledgeId)
}

function handleMoveKnowledge(knowledgeId: string, folderId: string) {
  const knowledge = knowledgeData.value.find(({ id }) => id === knowledgeId)
  if (knowledge) knowledge.folder_id = folderId
}
/* 批量选择与操作 */
const batchSelectionMode = ref(false)
const selectedKnowledgeIds = ref<string[]>([])
const selectedKnowledgeCount = computed(() => selectedKnowledgeIds.value.length)
const knowledgeIds = computed(() => knowledgeData.value.map(({ id }) => id))
const batchMoveToDialogRef = useTemplateRef<{ close: () => void; open: (currentFolderId?: string) => void }>('batchMoveToDialogRef')

function toggleBatchSelection() {
  batchSelectionMode.value = !batchSelectionMode.value
  selectedKnowledgeIds.value = []
}

function cancelBatchSelection() {
  batchSelectionMode.value = false
  selectedKnowledgeIds.value = []
}

function handleKnowledgeSelect(knowledgeId: string, selected: boolean) {
  if (selected) {
    if (!selectedKnowledgeIds.value.includes(knowledgeId)) selectedKnowledgeIds.value.push(knowledgeId)
    return
  }

  selectedKnowledgeIds.value = selectedKnowledgeIds.value.filter((id) => id !== knowledgeId)
}

function handleOpenBatchMove() {
  if (isShared.value || knowledgeOperationLoading.value || !selectedKnowledgeCount.value) return
  batchMoveToDialogRef.value?.open(currentFolder.value.id)
}

// 批量移动
function handleBatchMove(targetFolderId: string) {
  if (isShared.value || knowledgeOperationLoading.value || !selectedKnowledgeCount.value) return
  const knowledgeIds = [...selectedKnowledgeIds.value]

  knowledgeOperationLoading.value = true
  return KnowledgeApi.putBatchMoveKnowledge(knowledgeIds, targetFolderId)
    .then(() => {
      MsgSuccess('转移成功')
      batchMoveToDialogRef.value?.close()
      cancelBatchSelection()
      return refreshKnowledge()
    })
    .finally(() => {
      knowledgeOperationLoading.value = false
    })
}

// 批量操作
function handleBatchDelete() {
  if (isShared.value || knowledgeOperationLoading.value || !selectedKnowledgeCount.value) return
  const knowledgeIds = [...selectedKnowledgeIds.value]

  MsgConfirm(`是否批量删除 ${knowledgeIds.length} 个知识库？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      knowledgeOperationLoading.value = true
      return KnowledgeApi.putBatchDeleteKnowledge(knowledgeIds).then(() => {
        MsgSuccess('删除成功')
        cancelBatchSelection()
        return refreshKnowledge()
      })
    })
    .catch(() => {})
    .finally(() => {
      knowledgeOperationLoading.value = false
    })
}
</script>

<template>
  <MkViewLayout class="workspace-knowledge-view" collapsible>
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkTooltip content="创建文件夹" placement="top">
          <el-button text type="primary" class="-mr-1" @click="handleCreateFolder">
            <MkIcon name="icon_add-folder_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>

      <FolderTree ref="folderTreeRef" :source="RESOURCE_TYPE.KNOWLEDGE" draggable @select="handleFolderSelect" />
    </template>

    <template #default="{ Footer, Header }">
      <component :is="Header">
        <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <template v-if="!isShared">
            <span>
              <!-- 批量选择 -->
              <el-button :type="batchSelectionMode ? 'primary' : undefined" :disabled="!knowledgeData.length" plain @click="toggleBatchSelection">
                <MkIcon name="icon_Batch_outlined" />
                <span>{{ batchSelectionMode ? '取消选择' : '批量选择' }}</span>
              </el-button>
            </span>
            <template v-if="!batchSelectionMode">
              <!-- 模板中心 -->
              <ButtonTemplateStore :folder-id="createFolderId" @refresh="refreshKnowledge" />
              <!-- 创建 -->
              <ButtonCreateKnowledge :folder-id="createFolderId" @refresh="refreshKnowledge" />
            </template>
          </template>
        </div>
      </component>

      <div v-loading="knowledgeOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="knowledgeData" :load="loadKnowledgePage">
          <div class="mk-resource-card-grid">
            <template v-for="knowledge in knowledgeData" :key="knowledge.id">
              <KnowledgeCard
                :knowledge="knowledge"
                :shared="isShared"
                :selectable="batchSelectionMode"
                :selected="selectedKnowledgeIds.includes(knowledge.id)"
                @click="handleOpenKnowledge(knowledge)"
                @selected="handleKnowledgeSelect(knowledge.id, $event)"
              >
                <template v-if="!isShared" #action-dropdown>
                  <!-- TODO 同步 -->
                  <!-- TODO 向量化 -->
                  <!-- TODO 生成问题 -->
                  <!-- 设置 -->
                  <SettingKnowledgeAction label="设置" :knowledge="knowledge" />
                  <!-- 分词索引 -->
                  <KeywordIndexKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="分词索引"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- MCP 配置详情 -->
                  <McpConfigKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="MCP 配置详情"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 资源授权 -->
                  <AuthorizeKnowledgeAction label="资源授权" :knowledge="knowledge" />

                  <!-- 查看关联资源 -->
                  <RelatedResourcesKnowledgeAction label="查看关联资源" :api="RelatedResourcesApi" :knowledge="knowledge" />
                  <!-- 转移到 -->
                  <MoveKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="转移到"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                    :current-folder-id="currentFolder.id"
                    @delete="handleDeleteKnowledge"
                    @move="handleMoveKnowledge"
                  />

                  <!-- 导出 -->
                  <ExportKnowledgeAction v-model:loading="knowledgeOperationLoading" label="导出" :api="KnowledgeApi" :knowledge="knowledge" />
                  <!-- 删除 -->
                  <DeleteKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="删除"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                    @delete="handleDeleteKnowledge"
                  />
                </template>
              </KnowledgeCard>
            </template>
          </div>
          <template #empty>
            <MkEmpty class="mt-24" />
          </template>
        </MkInfiniteScroll>
      </div>
      <component
        :is="Footer"
        v-if="batchSelectionMode && !isShared"
        v-model:batch-selection="selectedKnowledgeIds"
        :batch-values="knowledgeIds"
        @batch-cancel="cancelBatchSelection"
      >
        <template #footer-batch-actions>
          <el-button type="primary" plain :disabled="knowledgeOperationLoading || !selectedKnowledgeCount" @click="handleOpenBatchMove"
            >转移到</el-button
          >
          <el-button type="danger" plain :disabled="knowledgeOperationLoading || !selectedKnowledgeCount" @click="handleBatchDelete">删除</el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>

  <MoveToDialog ref="batchMoveToDialogRef" :loading="knowledgeOperationLoading" :source="RESOURCE_TYPE.KNOWLEDGE" @submit="handleBatchMove" />
</template>
