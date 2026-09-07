<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedApi from '@/api/admin/workspace/shared'
import type { FolderItem, KnowledgeItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants/folder'
import FolderTree from '@/components/business/folder-tree/index.vue'
import KnowledgeCard from '@/views/knowledge/knowledge-card/KnowledgeCard.vue'

defineOptions({ name: 'SelectKnowledgeDialog' })

const emit = defineEmits<{ submit: [knowledge: (Partial<KnowledgeItem> & { id: string })[]] }>()
const visible = ref(false)
const loading = ref(false)
const searchKeyword = ref('')
const appliedSearchKeyword = ref('')
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.KNOWLEDGE].all })
const knowledgeOptions = ref<KnowledgeItem[]>([])
const selectedKnowledge = ref<(Partial<KnowledgeItem> & { id: string })[]>([])
const knowledgeLayoutRef = useTemplateRef<{ setScrollTop: (scrollTop: number) => void }>('knowledgeLayoutRef')
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
let dialogVersion = 0

// 与 v2 一致，以首个已选知识库的 Embedding 模型筛选可选资源。
const selectedKnowledgeIds = computed(() => selectedKnowledge.value.map(({ id }) => id))
const embeddingModelId = computed(() => selectedKnowledge.value.find((knowledge) => knowledge.embedding_model_id)?.embedding_model_id)
const filteredKnowledge = computed(() =>
  embeddingModelId.value
    ? knowledgeOptions.value.filter((knowledge) => knowledge.embedding_model_id === embeddingModelId.value)
    : knowledgeOptions.value,
)

function toggleKnowledge(knowledge: KnowledgeItem) {
  selectedKnowledge.value = selectedKnowledgeIds.value.includes(knowledge.id)
    ? selectedKnowledge.value.filter(({ id }) => id !== knowledge.id)
    : [...selectedKnowledge.value, cloneDeep(knowledge)]
}

// 每次查询一次加载全部结果，忽略切换目录或关闭弹窗前发出的旧请求。
function refreshKnowledge() {
  const version = ++dialogVersion
  loading.value = true
  knowledgeOptions.value = []
  appliedSearchKeyword.value = searchKeyword.value.trim()
  const shared = currentFolder.value.id === FOLDER_ENTRY_ID.SHARED
  const requestApi = shared ? SharedApi : KnowledgeApi
  return requestApi
    .getAllKnowledge({
      ...(shared ? {} : { folder_id: currentFolder.value.id }),
      ...(appliedSearchKeyword.value ? { name: appliedSearchKeyword.value } : {}),
    })
    .then((knowledge) => {
      if (version !== dialogVersion) return
      knowledgeOptions.value = knowledge
      // 仅补全已选快照，不因查询结果缺少某个 ID 而删除关联。
      const knowledgeById = new Map(knowledge.map((knowledge) => [knowledge.id, knowledge]))
      selectedKnowledge.value = selectedKnowledge.value.map((knowledge) => knowledgeById.get(knowledge.id) ?? knowledge)
      return nextTick(() => {
        if (version === dialogVersion) knowledgeLayoutRef.value?.setScrollTop(0)
      })
    })
    .finally(() => {
      if (version === dialogVersion) loading.value = false
    })
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

function open(knowledge: (Partial<KnowledgeItem> & { id: string })[]) {
  selectedKnowledge.value = cloneDeep(knowledge)
  visible.value = true
  void refreshKnowledge()
}

function submit() {
  emit('submit', cloneDeep(selectedKnowledge.value))
  visible.value = false
}
function resetData() {
  dialogVersion++
  loading.value = false
  searchKeyword.value = ''
  appliedSearchKeyword.value = ''
  currentFolder.value = { ...FOLDER_ENTRIES[RESOURCE_TYPE.KNOWLEDGE].all }
  knowledgeOptions.value = []
  selectedKnowledge.value = []
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" align-center class="mk-aside-content-dialog" title="关联知识库" width="1200" @closed="resetData">
    <template #header="{ titleId }">
      <div class="flex-between pr-8">
        <div class="flex items-center gap-2">
          <h4 :id="titleId">关联知识库</h4>
          <span class="text-N600!">所选知识库必须使用相同的 Embedding 模型</span>
        </div>

        <el-button text class="h-7! w-7! min-w-0! p-1!" title="刷新" aria-label="刷新知识库" @click="refreshResources">
          <MkIcon name="icon_refresh_outlined" :size="20" />
        </el-button>
      </div>
    </template>

    <MkViewLayout ref="knowledgeLayoutRef" :loading="loading" title="">
      <template #aside>
        <FolderTree
          ref="folderTreeRef"
          class="pt-4"
          :can-edit="false"
          :source="RESOURCE_TYPE.KNOWLEDGE"
          @loaded="selectFolder"
          @select="selectFolder"
        />
      </template>
      <template #default="{ Header }">
        <component :is="Header">
          <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
          <MkSearchInput v-model="searchKeyword" class="w-60! shrink-0" @change="refreshKnowledge" />
        </component>

        <template v-if="!loading">
          <div v-if="filteredKnowledge.length" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <template v-for="knowledge in filteredKnowledge" :key="knowledge.id">
              <el-popover placement="bottom-start" :width="360" :show-after="500" :persistent="false" popper-class="border-none! rounded-xl!">
                <template #reference>
                  <el-card
                    shadow="hover"
                    class="min-w-0 cursor-pointer"
                    :class="{ 'border-primary!': selectedKnowledgeIds.includes(knowledge.id) }"
                    @click="toggleKnowledge(knowledge)"
                  >
                    <div class="flex-between gap-3">
                      <div class="flex min-w-0 flex-1 items-center gap-2">
                        <KnowledgeIcon :type="knowledge.type" class="shrink-0" />
                        <span class="min-w-0 flex-1 truncate" :title="knowledge.name">{{ knowledge.name }}</span>
                      </div>
                      <el-checkbox
                        :model-value="selectedKnowledgeIds.includes(knowledge.id)"
                        :aria-label="knowledge.name"
                        class="shrink-0"
                        @click.stop
                        @change="toggleKnowledge(knowledge)"
                      />
                    </div>
                  </el-card>
                </template>
                <template #default>
                  <KnowledgeCard :knowledge="knowledge" disabled> </KnowledgeCard>
                </template>
              </el-popover>
            </template>
          </div>
          <MkEmpty v-else class="mt-24" :type="appliedSearchKeyword ? 'search' : 'default'" />
        </template>
      </template>
    </MkViewLayout>
    <template #footer>
      <div class="flex-between -mx-6 border-t px-6 pt-4">
        <div class="flex items-center gap-2">
          <span class="text-N600">已选 {{ selectedKnowledge.length }}</span>
          <el-button v-if="selectedKnowledge.length" link type="primary" @click="selectedKnowledge = []">清空</el-button>
        </div>
        <div>
          <el-button plain @click="visible = false">取消</el-button>
          <el-button type="primary" @click="submit">确定</el-button>
        </div>
      </div>
    </template>
  </MkDialog>
</template>
