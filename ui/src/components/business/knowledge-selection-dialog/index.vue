<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { Refresh } from '@element-plus/icons-vue'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedApi from '@/api/admin/workspace/shared'
import type { ParamsPage } from '@/api/admin/core/types'
import type { FolderItem, KnowledgeItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants/folder'
import FolderTree from '@/components/business/folder-tree/index.vue'
import type { KnowledgeSelection } from './types'

defineOptions({ name: 'KnowledgeSelectionDialog' })

const emit = defineEmits<{ submit: [knowledge: KnowledgeSelection[]] }>()
const visible = ref(false)
const searchKeyword = ref('')
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.KNOWLEDGE].all })
const knowledgeOptions = ref<KnowledgeItem[]>([])
const selectedKnowledge = ref<KnowledgeSelection[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
let dialogVersion = 0

// 以已选知识库确定 Embedding 模型，跨文件夹、搜索和分页保留选择。
const embeddingModelId = computed(() => selectedKnowledge.value.find((knowledge) => knowledge.embedding_model_id)?.embedding_model_id)

function isSelected(id: string) {
  return selectedKnowledge.value.some((knowledge) => knowledge.id === id)
}

function isDisabled(knowledge: KnowledgeItem) {
  return !isSelected(knowledge.id) && Boolean(embeddingModelId.value && knowledge.embedding_model_id !== embeddingModelId.value)
}

function toggleKnowledge(knowledge: KnowledgeItem) {
  if (isDisabled(knowledge)) return
  selectedKnowledge.value = isSelected(knowledge.id)
    ? selectedKnowledge.value.filter(({ id }) => id !== knowledge.id)
    : [...selectedKnowledge.value, cloneDeep(knowledge)]
}

function loadKnowledgePage(pagination: ParamsPage) {
  const version = dialogVersion
  const shared = currentFolder.value.id === FOLDER_ENTRY_ID.SHARED
  const requestApi = shared ? SharedApi : KnowledgeApi
  return requestApi
    .getKnowledgePage(pagination, {
      ...(shared ? {} : { folder_id: currentFolder.value.id }),
      ...(searchKeyword.value.trim() ? { name: searchKeyword.value.trim() } : {}),
    })
    .then((page) => {
      if (version === dialogVersion) {
        // 仅补全已选快照，不因当前页或查询结果缺少某个 ID 而删除关联。
        const knowledgeById = new Map(page.records.map((knowledge) => [knowledge.id, knowledge]))
        selectedKnowledge.value = selectedKnowledge.value.map((knowledge) => knowledgeById.get(knowledge.id) ?? knowledge)
      }
      return page
    })
}

function refreshKnowledge() {
  return infiniteScrollRef.value?.reset()
}

function refreshResources() {
  folderTreeRef.value?.refresh()
  void refreshKnowledge()
}

function selectFolder(folder?: FolderItem) {
  if (!folder || folder.id === currentFolder.value.id) return
  currentFolder.value = folder
  void refreshKnowledge()
}

// 弹窗只在确认后向调用方提交，取消和关闭统一清理临时状态。
function resetData() {
  dialogVersion++
  searchKeyword.value = ''
  currentFolder.value = { ...FOLDER_ENTRIES[RESOURCE_TYPE.KNOWLEDGE].all }
  knowledgeOptions.value = []
  selectedKnowledge.value = []
}

function open(knowledge: KnowledgeSelection[]) {
  resetData()
  selectedKnowledge.value = cloneDeep(knowledge)
  visible.value = true
}

function submit() {
  emit('submit', cloneDeep(selectedKnowledge.value))
  visible.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="添加关联知识库" width="960" @closed="resetData">
    <template #subtitle>所选知识库必须使用相同的 Embedding 模型</template>
    <div class="flex h-105 gap-4">
      <div class="w-55 shrink-0 border-r">
        <FolderTree ref="folderTreeRef" :can-edit="false" :source="RESOURCE_TYPE.KNOWLEDGE" @loaded="selectFolder" @select="selectFolder" />
      </div>
      <div class="flex min-w-0 flex-1 flex-col gap-3">
        <div class="flex-between gap-3">
          <h6 class="truncate" :title="currentFolder.name">{{ currentFolder.name }}</h6>
          <div class="flex items-center gap-2">
            <MkSearchInput v-model="searchKeyword" placeholder="搜索知识库" @change="refreshKnowledge" />
            <el-button text title="刷新" @click="refreshResources"><MkIcon :icon="Refresh" /></el-button>
          </div>
        </div>
        <el-scrollbar class="flex-1">
          <MkInfiniteScroll ref="infiniteScrollRef" v-model="knowledgeOptions" :load="loadKnowledgePage">
            <div class="grid grid-cols-2 gap-2 pr-2">
              <el-checkbox
                v-for="knowledge in knowledgeOptions"
                :key="knowledge.id"
                :model-value="isSelected(knowledge.id)"
                :disabled="isDisabled(knowledge)"
                class="m-0! h-auto! min-w-0 rounded-md border p-3! [&_.el-checkbox__label]:min-w-0"
                @change="toggleKnowledge(knowledge)"
              >
                <span class="flex min-w-0 items-center gap-2">
                  <KnowledgeIcon :type="knowledge.type" :size="24" class="shrink-0" />
                  <span class="min-w-0">
                    <span class="block truncate" :title="knowledge.name">{{ knowledge.name }}</span>
                    <span v-if="knowledge.desc" class="block truncate text-sm text-N600" :title="knowledge.desc">{{ knowledge.desc }}</span>
                  </span>
                </span>
              </el-checkbox>
            </div>
            <template #empty><MkEmpty :type="searchKeyword ? 'search' : 'default'" /></template>
          </MkInfiniteScroll>
        </el-scrollbar>
      </div>
    </div>
    <template #footer>
      <div class="flex-between">
        <div class="flex items-center gap-2">
          <span class="text-N600">已选择 {{ selectedKnowledge.length }} 项</span>
          <el-button v-if="selectedKnowledge.length" link type="primary" @click="selectedKnowledge = []">清空</el-button>
        </div>
        <div>
          <el-button @click="visible = false">取消</el-button>
          <el-button type="primary" @click="submit">确定</el-button>
        </div>
      </div>
    </template>
  </MkDialog>
</template>
