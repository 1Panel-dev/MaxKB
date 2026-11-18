<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { Dict, FolderItem, KnowledgeItem, OptionItem } from '@/api/types'
import { KNOWLEDGE_TYPE, RESOURCE_TYPE } from '@/api/enums'
import CommonSystemApi from '@/api/admin/system/common'
import CommonApi from '@/api/admin/workspace/common'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import RelatedResourcesApi from '@/api/admin/workspace/related-resources'
import SharedKnowledgeApi from '@/api/admin/workspace/shared/knowledge/knowledge.ts'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import FolderTree from '@/components/business/folder-tree/index.vue'
import ButtonCreateKnowledge from './components/ButtonCreateKnowledge.vue'
import ButtonTemplateStore from './components/ButtonTemplateStore.vue'
import KnowledgeCard from './knowledge-card/KnowledgeCard.vue'
import {
  AuthorizeKnowledgeAction,
  DeleteKnowledgeAction,
  EmbeddingKnowledgeAction,
  ExportKnowledgeAction,
  GenerateQuestionsAction,
  KeywordIndexKnowledgeAction,
  McpConfigKnowledgeAction,
  MoveKnowledgeAction,
  RelatedResourcesKnowledgeAction,
  SyncKnowledgeAction,
} from './knowledge-card/action-dropdown'
import { FOLDER_ENTRY_ID } from '@/constants/folder'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { perm } from '@/permission'

const { t } = useI18n({ useScope: 'global' })

/* 知识库详情入口 */
const route = useRoute()
const router = useRouter()

function handleOpenKnowledge(knowledge: KnowledgeItem) {
  void router.push({
    name: isShared.value ? 'workspace-shared-knowledge-detail' : 'workspace-knowledge-detail',
    params: { workspaceId: route.params.workspaceId, knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type] },
  })
}

function handleOpenKnowledgeSetting(knowledge: KnowledgeItem) {
  void router.push({
    name: knowledge.type === KNOWLEDGE_TYPE.BASE ? 'workspace-knowledge-setting' : 'workspace-knowledge-base-setting',
    params: { workspaceId: route.params.workspaceId, knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type] },
  })
}

/* 当前文件夹 */
const currentFolderId = ref<string>(FOLDER_ENTRY_ID.ALL)
const selectedFolder = ref<FolderItem>()
const currentFolder = computed<FolderItem>(() => selectedFolder.value ?? { id: FOLDER_ENTRY_ID.ALL, name: t('knowledge.categories.all') })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder?: FolderItem) {
  const previousFolderId = currentFolder.value.id
  selectedFolder.value = folder
  currentFolderId.value = currentFolder.value.id
  if (previousFolderId !== currentFolderId.value) {
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
  { label: t('common.name.label'), value: 'name' },
  {
    label: t('common.labels.type'),
    value: 'type',
    options: [
      { value: KNOWLEDGE_TYPE.BASE, label: t('knowledge.base.label') },
      { value: KNOWLEDGE_TYPE.WEB, label: t('knowledge.web.label') },
      { value: KNOWLEDGE_TYPE.LARK, label: t('knowledge.lark.label') },
      { value: KNOWLEDGE_TYPE.WORKFLOW, label: t('knowledge.workflow.label') },
    ],
  },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
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
      MsgSuccess(t('common.messages.moveSuccess'))
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

  MsgConfirm(`${t('knowledge.delete.batchTitle')} (${knowledgeIds.length})?`, t('common.dialogs.deleteWarning'))
    .then(() => {
      knowledgeOperationLoading.value = true
      return KnowledgeApi.putBatchDeleteKnowledge(knowledgeIds).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
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
  <MkViewLayout :title="t('knowledge.title')" class="workspace-knowledge-view" collapsible resizable>
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkTooltip v-if="perm.knowledge.workspace.folderCreateWorkspace()" :content="t('folder.actions.create')" placement="top">
          <el-button text type="primary" class="-mr-1" @click="handleCreateFolder">
            <MkIcon name="icon_add-folder_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>

      <FolderTree
        ref="folderTreeRef"
        v-model="currentFolderId"
        :source="RESOURCE_TYPE.KNOWLEDGE"
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
          <template v-if="!isShared">
            <span>
              <!-- 批量选择 -->
              <el-button
                v-if="perm.knowledge.workspace.batchDelete() || perm.knowledge.workspace.batchMove()"
                :type="batchSelectionMode ? 'primary' : undefined"
                :disabled="!knowledgeData.length"
                plain
                @click="toggleBatchSelection"
              >
                <MkIcon name="icon_Batch_outlined" />
                <span>{{ batchSelectionMode ? t('common.actions.cancelSelection') : t('common.actions.batchSelect') }}</span>
              </el-button>
            </span>
            <template v-if="!batchSelectionMode">
              <!-- 模板中心 -->
              <ButtonTemplateStore :folder-id="createFolderId" @refresh="refreshKnowledge" />
              <!-- 创建 -->
              <ButtonCreateKnowledge v-if="perm.knowledge.workspace.create()" :folder-id="createFolderId" @refresh="refreshKnowledge" />
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
                :disabled="isShared"
                :selectable="batchSelectionMode"
                :selected="selectedKnowledgeIds.includes(knowledge.id)"
                @click="handleOpenKnowledge(knowledge)"
                @selected="handleKnowledgeSelect(knowledge.id, $event)"
              >
                <template v-if="!isShared" #action-dropdown>
                  <!-- 同步 Web 知识库 -->
                  <SyncKnowledgeAction
                    v-if="knowledge.type === KNOWLEDGE_TYPE.WEB && perm.knowledge.workspace.sync(knowledge.id)"
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.actions.sync')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 向量化 -->
                  <EmbeddingKnowledgeAction
                    v-if="perm.knowledge.workspace.vector(knowledge.id)"
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.actions.generateEmbeddings')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 生成问题 -->
                  <GenerateQuestionsAction
                    v-if="perm.knowledge.workspace.generate(knowledge.id)"
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.actions.generateQuestions')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                  />

                  <!-- 设置 -->
                  <MkDropdownItem v-if="perm.knowledge.workspace.settingRead(knowledge.id)" @click.stop="handleOpenKnowledgeSetting(knowledge)">
                    <template #icon><MkIcon name="icon_setting" /></template>
                    {{ t('common.labels.settings') }}
                  </MkDropdownItem>
                  <!-- 分词索引 -->
                  <KeywordIndexKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.actions.buildKeywordIndex')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                    v-if="perm.knowledge.workspace.token(knowledge.id)"
                  />
                  <!-- MCP 服务配置 -->
                  <McpConfigKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('resource.mcpConfig.title')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                    v-if="perm.knowledge.workspace.mcpConfig(knowledge.id)"
                  />
                  <!-- 资源授权 -->
                  <AuthorizeKnowledgeAction
                    v-if="perm.knowledge.workspace.auth(knowledge.id)"
                    :label="t('resource.authorization.title')"
                    :knowledge="knowledge"
                  />

                  <!-- 查看关联资源 -->
                  <RelatedResourcesKnowledgeAction
                    v-if="perm.knowledge.workspace.relateMap(knowledge.id)"
                    :label="t('resource.relations.title')"
                    :api="RelatedResourcesApi"
                    :knowledge="knowledge"
                  />
                  <!-- 移动到 -->
                  <MoveKnowledgeAction
                    v-if="perm.knowledge.workspace.move(knowledge.id)"
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('folder.actions.moveTo')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                    :current-folder-id="currentFolder.id"
                    @delete="handleDeleteKnowledge"
                    @move="handleMoveKnowledge"
                  />

                  <!-- 导出 -->
                  <ExportKnowledgeAction
                    v-if="perm.knowledge.workspace.export(knowledge.id)"
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('common.actions.export')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 删除 -->
                  <DeleteKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('common.actions.delete')"
                    :api="KnowledgeApi"
                    :knowledge="knowledge"
                    @delete="handleDeleteKnowledge"
                    v-if="perm.knowledge.workspace.delete(knowledge.id)"
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
          <el-button
            type="primary"
            v-if="perm.knowledge.workspace.batchMove()"
            plain
            :disabled="knowledgeOperationLoading || !selectedKnowledgeCount"
            @click="handleOpenBatchMove"
          >
            {{ t('folder.actions.moveTo') }}
          </el-button>
          <el-button
            type="danger"
            v-if="perm.knowledge.workspace.batchDelete()"
            plain
            :disabled="knowledgeOperationLoading || !selectedKnowledgeCount"
            @click="handleBatchDelete"
          >
            {{ t('common.actions.delete') }}
          </el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>

  <MoveToDialog ref="batchMoveToDialogRef" :loading="knowledgeOperationLoading" :source="RESOURCE_TYPE.KNOWLEDGE" @submit="handleBatchMove" />
</template>
