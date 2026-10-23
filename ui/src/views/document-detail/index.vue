<script setup lang="ts">
import { computed, nextTick, onMounted, ref, type Directive } from 'vue'
import { useRoute } from 'vue-router'
import type MkViewLayout from '@/components/global/mk-view-layout/index.vue'
import { provideDocumentDetailContext } from './context'
import type { ParamsPage } from '@/api/admin/core/types'
import type { DocumentItem, ParagraphItem, ParagraphQuery } from '@/api/types'
import { getFileIconUrl } from '@/utils/icon'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { useParagraphSort } from './action-dropdown/move/useParagraphSort'
import CreateParagraphDialog from './paragraph-dialog/CreateParagraphDialog.vue'
import EditParagraphDialog from './paragraph-dialog/ParagraphDialog.vue'
import {
  BatchMigrateParagraphAction,
  MigrateParagraphAction,
  BatchGenerateQuestionsAction,
  GenerateQuestionsAction,
  MoveParagraphAction,
} from './action-dropdown'
import { isWorkspaceSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'KnowledgeParagraphView' })

/* 文档详情与分段查询 */
const route = useRoute()
const { resourceApi, handleBack } = provideDocumentDetailContext()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))
const documentId = computed(() => String(route.params.documentId ?? ''))
const documentDetail = ref<DocumentItem>()
const paragraphs = ref<ParagraphItem[]>([])
const infiniteScrollRef = ref<{ reset: () => Promise<void> }>()
const paragraphTotal = ref(0)
const loading = ref(false)
const paragraphQuery = ref<ParagraphQuery>({})
const searchFields = [
  { label: '标题', value: 'title' },
  { label: '内容', value: 'content' },
]

function loadParagraphPage(pagination: ParamsPage) {
  return resourceApi.paragraph.getParagraphPage(knowledgeId.value, documentId.value, pagination, paragraphQuery.value).then((page) => {
    paragraphTotal.value = page.total
    return page
  })
}

function refreshParagraphs() {
  selectedParagraphIds.value = []
  openParagraphMenuIds.value = { more: '', position: '' }
  paragraphTotal.value = 0
  layoutRef.value?.setScrollTop(0)
  return infiniteScrollRef.value?.reset()
}

function handleSearchChange(query?: ParagraphQuery) {
  if (loading.value) return
  paragraphQuery.value = query ?? {}
  void refreshParagraphs()
}

/* 分段目录定位与滚动高亮 */
const layoutRef = ref<InstanceType<typeof MkViewLayout>>()
const paragraphScrollContainer = computed(() => layoutRef.value?.getScrollContainer())
// AnchorLink 的 a 在组件内部渲染，只关闭链接原生拖动，排序行仍由 Sortable 管理。
const vDisableLinkDrag: Directive<HTMLElement> = {
  mounted(element) {
    element.querySelector('a')?.setAttribute('draggable', 'false')
  },
}

/* 批量选择已加载的分段 */
const batchMode = ref(false)
const selectedParagraphIds = ref<string[]>([])
const paragraphIds = computed(() => paragraphs.value.map(({ id }) => id))

function handleToggleBatchMode() {
  if (loading.value) return
  batchMode.value = !batchMode.value
  selectedParagraphIds.value = []
  openParagraphMenuIds.value = { more: '', position: '' }
}

function handleSelectBatchParagraph(paragraphId: string, selected: boolean) {
  if (loading.value) return
  selectedParagraphIds.value = selected ? [...selectedParagraphIds.value, paragraphId] : selectedParagraphIds.value.filter((id) => id !== paragraphId)
}

function handleClickParagraphCard(paragraph: ParagraphItem) {
  if (loading.value) return
  if (batchMode.value) {
    handleSelectBatchParagraph(paragraph.id, !selectedParagraphIds.value.includes(paragraph.id))
    return
  }
  return handleOpenParagraphDetail(paragraph)
}

// 编辑和启停共用局部替换，编辑后不再匹配搜索条件时刷新列表。
function handleReplaceParagraph(paragraph: ParagraphItem) {
  const paragraphIndex = paragraphs.value.findIndex(({ id }) => id === paragraph.id)
  if (paragraphIndex < 0) return
  const matchesQuery = Object.entries(paragraphQuery.value).every(([field, keyword]) =>
    (paragraph[field as keyof ParagraphQuery] ?? '').toLowerCase().includes(keyword.toLowerCase()),
  )
  if (!matchesQuery) {
    return refreshParagraphs()
  }
  paragraphs.value.splice(paragraphIndex, 1, paragraph)
}

// 生成问题为异步任务，提交成功只清空选择，不重新查询分段列表。
function handleGenerateQuestionsSuccess() {
  selectedParagraphIds.value = []
}

// 批量删除：确认前固定目标，取消或失败保留勾选。
function handleBatchDeleteParagraphs() {
  if (loading.value || !selectedParagraphIds.value.length) return
  const targetParagraphIds = [...selectedParagraphIds.value]
  const targetKnowledgeId = knowledgeId.value
  const targetDocumentId = documentId.value
  loading.value = true
  return MsgConfirm(`确认删除选中的 ${targetParagraphIds.length} 个分段？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      return resourceApi.paragraph.putBatchDeleteParagraphs?.(targetKnowledgeId, targetDocumentId, targetParagraphIds).then(() => {
        MsgSuccess('删除成功')
        return refreshParagraphs()
      })
    })
    .catch(() => {
      // 取消无需提示，请求失败由请求层统一提示。
    })
    .finally(() => {
      loading.value = false
    })
}

/* 分段弹窗按需挂载；新增重置列表，编辑局部替换。 */
const createDialogMounted = ref(false)
const createDialogRef = ref<InstanceType<typeof CreateParagraphDialog>>()
const editDialogMounted = ref(false)
const editDialogRef = ref<InstanceType<typeof EditParagraphDialog>>()
const searchKey = ref(0)

async function handleOpenCreateParagraph(position?: number) {
  if (loading.value) return
  createDialogMounted.value = true
  await nextTick()
  createDialogRef.value?.open(position)
}

async function handleOpenParagraphDetail(paragraph: ParagraphItem, initialMode: 'detail' | 'edit' = 'detail') {
  if (loading.value) return
  editDialogMounted.value = true
  await nextTick()
  editDialogRef.value?.open(paragraph, initialMode)
}

/* 单个分段启停、删除与位置调整；写入成功后再更新页面。 */
// 菜单弹层不在卡片内部，展开期间保持对应分段的悬浮操作区可见。
const openParagraphMenuIds = ref({ more: '', position: '' })

function handleParagraphMenuVisibleChange(paragraphId: string, menu: 'more' | 'position', visible: boolean) {
  if (visible) openParagraphMenuIds.value[menu] = paragraphId
  else if (openParagraphMenuIds.value[menu] === paragraphId) openParagraphMenuIds.value[menu] = ''
}

function handleToggleParagraph(paragraph: ParagraphItem) {
  if (loading.value) return false
  loading.value = true
  return (
    resourceApi.paragraph
      .putParagraph?.(knowledgeId.value, documentId.value, paragraph.id, { is_active: !paragraph.is_active })
      .then((updatedParagraph) => {
        handleReplaceParagraph(updatedParagraph)
        MsgSuccess('操作成功')
        // 服务端响应已更新受控开关，阻止 before-change 再触发一次切换。
        return false
      })
      .catch(() => false) ?? Promise.resolve(false)
  ).finally(() => {
    loading.value = false
  })
}

function handleDeleteParagraph(paragraph: ParagraphItem) {
  if (loading.value) return
  const targetKnowledgeId = knowledgeId.value
  const targetDocumentId = documentId.value
  const targetParagraphId = paragraph.id
  loading.value = true
  return MsgConfirm(`是否删除分段：${paragraph.title || '-'}？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      return resourceApi.paragraph.deleteParagraph?.(targetKnowledgeId, targetDocumentId, targetParagraphId).then(() => {
        MsgSuccess('删除成功')
        return refreshParagraphs()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

/* 左侧目录与右侧卡片共用分段数组和位置保存流程。 */
const paragraphCardsRef = ref<HTMLElement>()
const paragraphDirectoryRef = ref<HTMLElement>()
const paragraphSortDisabled = computed(
  () =>
    isWorkspaceSharedResource() ||
    loading.value ||
    batchMode.value ||
    createDialogMounted.value ||
    editDialogMounted.value ||
    paragraphs.value.length < 2,
)
const { handleMoveParagraph } = useParagraphSort({
  paragraphs,
  loading,
  disabled: paragraphSortDisabled,
  directoryRef: paragraphDirectoryRef,
  cardsRef: paragraphCardsRef,
  knowledgeId,
  documentId,
  resourceApi,
  onStart: () => {
    openParagraphMenuIds.value = { more: '', position: '' }
  },
})

function handleCreateParagraphSuccess() {
  paragraphQuery.value = {}
  searchKey.value += 1
  return refreshParagraphs()
}

onMounted(() => {
  loading.value = true
  void (
    resourceApi.document
      .getDocumentDetail?.(knowledgeId.value, documentId.value)
      .then((document) => {
        documentDetail.value = document
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
})
</script>

<template>
  <MkViewLayout ref="layoutRef" title="" :loading="loading" collapsible class="[&_aside+button]:top-4!">
    <template #top>
      <div class="flex-between gap-4" :inert="loading">
        <div class="flex-align-center min-w-0 gap-2">
          <!-- 返回文档列表 -->
          <el-button text @click="handleBack"><MkIcon name="icon_arrow-left_outlined" :size="20" /></el-button>
          <template v-if="documentDetail">
            <img v-if="route.params.type === KNOWLEDGE_TYPE_KEY.WEB" src="@/assets/file-type/web-link-icon.svg" alt="" class="size-6 shrink-0" />
            <img v-else :src="getFileIconUrl(documentDetail.name)" alt="" class="size-6 shrink-0" />
          </template>
          <h4 class="truncate" :title="documentDetail?.name">{{ documentDetail?.name ?? '-' }}</h4>
        </div>
        <div class="flex-align-center shrink-0 gap-3">
          <MkComplexSearch :key="searchKey" :fields="searchFields" @change="handleSearchChange" />
          <!-- 切换批量选择 -->
          <span v-if="!isWorkspaceSharedResource()">
            <el-button :type="batchMode ? 'primary' : undefined" :disabled="!paragraphs.length" plain @click="handleToggleBatchMode">
              <MkIcon name="icon_Batch_outlined" />
              <span>{{ batchMode ? '取消选择' : '批量选择' }}</span>
            </el-button>
          </span>
          <!-- 添加文档分段 -->
          <el-button v-if="!isWorkspaceSharedResource() && !batchMode" type="primary" @click="handleOpenCreateParagraph()">
            <MkIcon name="icon_add_outlined" />
            <span>添加分段</span>
          </el-button>
        </div>
      </div>
    </template>
    <template #aside>
      <el-scrollbar class="min-h-0 flex-1" view-class="p-4">
        <el-anchor
          v-if="paragraphScrollContainer && paragraphs.length"
          ref="paragraphAnchorRef"
          :container="paragraphScrollContainer"
          :marker="false"
          :offset="24"
          select-scroll-top
          @click.prevent
        >
          <div ref="paragraphDirectoryRef">
            <template v-for="paragraph in paragraphs" :key="paragraph.id">
              <div class="paragraph-directory-row group relative">
                <!-- 拖拽排序分段目录；手柄与链接并列，避免触发链接原生拖动 -->
                <el-button
                  v-if="!batchMode"
                  link
                  class="paragraph-directory-drag-handle group-hover-visible absolute! top-1/2 -left-4 z-10 -translate-y-1/2 text-N600 h-8!"
                  :disabled="paragraphSortDisabled"
                  @click.prevent.stop
                >
                  <MkIcon name="icon_drag_outlined" />
                </el-button>
                <!-- 定位文档分段 -->
                <el-anchor-link v-disable-link-drag :href="`#paragraph-${paragraph.id}`">
                  <div
                    class="flex-align-center gap-2 rounded-md px-2 py-1 font-normal text-N600 hover:bg-N900/10 [.is-active_&]:text-primary"
                    :title="paragraph.title || ''"
                  >
                    <span class="min-w-0 flex-1 truncate">{{ paragraph.title || '-' }}</span>
                  </div>
                </el-anchor-link>
              </div>
            </template>
          </div>
        </el-anchor>
      </el-scrollbar>
    </template>

    <template #default="{ Header, Footer }">
      <component :is="Header">
        <p class="text-N600">{{ paragraphTotal }} 分段</p>
      </component>
      <MkInfiniteScroll ref="infiniteScrollRef" v-model="paragraphs" :load="loadParagraphPage">
        <div ref="paragraphCardsRef" class="space-y-3">
          <template v-for="paragraph in paragraphs" :key="paragraph.id">
            <div class="paragraph-sort-row group relative">
              <!-- 拖拽排序分段卡片 -->
              <el-button
                v-if="!batchMode"
                link
                class="paragraph-card-drag__handle group-hover-visible absolute! top-4 -left-5 z-10 text-N600 h-8!"
                :disabled="paragraphSortDisabled"
                @click.stop
              >
                <MkIcon name="icon_drag_outlined" />
              </el-button>
              <el-card
                :id="`paragraph-${paragraph.id}`"
                shadow="never"
                class="mk-paragraph-card relative cursor-pointer overflow-visible!"
                body-class="overflow-visible!"
                :class="{ selectable: batchMode, active: batchMode && selectedParagraphIds.includes(paragraph.id), disabled: !paragraph.is_active }"
                @click="handleClickParagraphCard(paragraph)"
              >
                <div
                  v-if="!isWorkspaceSharedResource() && !batchMode"
                  class="paragraph-card-actions sticky top-3 z-10 h-0"
                  :class="{ 'group-hover-visible': openParagraphMenuIds.more !== paragraph.id && openParagraphMenuIds.position !== paragraph.id }"
                  @click.stop
                >
                  <el-card class="absolute top-0 right-0" shadow="always" style="--el-card-padding: 4px">
                    <div class="flex-align-center">
                      <!-- 启用或禁用当前分段 -->
                      <el-switch
                        :model-value="paragraph.is_active"
                        :disabled="loading"
                        size="small"
                        class="ml-1"
                        :before-change="() => handleToggleParagraph(paragraph)"
                      />
                      <el-divider direction="vertical" class="ml-3! mr-2!" />
                      <MkTooltip content="编辑">
                        <!-- 编辑当前分段 -->
                        <el-button text @click="handleOpenParagraphDetail(paragraph, 'edit')">
                          <MkIcon name="icon_edit_outlined" />
                        </el-button>
                      </MkTooltip>
                      <MkTooltip content="上方插入分段">
                        <!-- 在当前分段上方插入 -->
                        <el-button text @click="handleOpenCreateParagraph(paragraph.position)">
                          <MkIcon name="icon_add_outlined-1" />
                        </el-button>
                      </MkTooltip>
                      <MkDropdown
                        trigger="click"
                        placement="bottom-end"
                        hide-when-empty
                        persistent
                        class="ml-1"
                        @visible-change="handleParagraphMenuVisibleChange(paragraph.id, 'more', $event)"
                      >
                        <!-- 展开分段更多操作 -->
                        <el-button text><MkIcon name="icon_more_outlined" /></el-button>
                        <template #dropdown>
                          <MkDropdownMenu>
                            <!-- 生成当前分段的问题 -->
                            <GenerateQuestionsAction
                              label="生成问题"
                              :api="resourceApi.paragraph"
                              :knowledge-id="knowledgeId"
                              :document-id="documentId"
                              :paragraph-id="paragraph.id"
                              :disabled="loading"
                              @refresh="handleGenerateQuestionsSuccess"
                            />
                            <!-- 迁移当前分段 -->
                            <MigrateParagraphAction
                              :api="resourceApi.paragraph"
                              :knowledge-id="knowledgeId"
                              :document-id="documentId"
                              :paragraph-id="paragraph.id"
                              :disabled="loading"
                              @success="refreshParagraphs"
                            />
                            <!-- 展开分段位置菜单 -->
                            <MoveParagraphAction
                              label="移动位置"
                              divided
                              :disabled="loading"
                              @move="handleMoveParagraph(paragraph, $event)"
                              @visible-change="handleParagraphMenuVisibleChange(paragraph.id, 'position', $event)"
                            />
                            <!-- 删除当前分段 -->
                            <MkDropdownItem divided :disabled="loading" @click="handleDeleteParagraph(paragraph)">
                              <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                              删除
                            </MkDropdownItem>
                          </MkDropdownMenu>
                        </template>
                      </MkDropdown>
                    </div>
                  </el-card>
                </div>
                <!-- 选择批量操作的分段 -->
                <el-checkbox
                  v-if="batchMode"
                  class="absolute! top-4 right-4"
                  :model-value="selectedParagraphIds.includes(paragraph.id)"
                  @click.stop
                  @change="(selected: boolean | string | number) => handleSelectBatchParagraph(paragraph.id, Boolean(selected))"
                />

                <h4 class="mb-2 pr-44">{{ paragraph.title || '-' }}</h4>
                <MdPreview :model-value="paragraph.content" />
                <p class="mt-2 text-sm text-N600">{{ paragraph.content.length }} 字符</p>
              </el-card>
            </div>
          </template>
        </div>
        <template #empty>
          <MkEmpty :type="Object.keys(paragraphQuery).length ? 'search' : 'default'" description="暂无分段" />
        </template>
      </MkInfiniteScroll>
      <component
        :is="Footer"
        v-if="batchMode"
        v-model:batch-selection="selectedParagraphIds"
        :batch-values="paragraphIds"
        @batch-cancel="batchMode = false"
      >
        <template #footer-batch-actions>
          <!-- 批量迁移分段 -->
          <BatchMigrateParagraphAction
            :api="resourceApi.paragraph"
            :knowledge-id="knowledgeId"
            :document-id="documentId"
            :paragraph-ids="selectedParagraphIds"
            :disabled="loading"
            @success="refreshParagraphs"
          />
          <!-- 批量生成问题 -->
          <BatchGenerateQuestionsAction
            :api="resourceApi.paragraph"
            :knowledge-id="knowledgeId"
            :document-id="documentId"
            :paragraph-ids="selectedParagraphIds"
            :disabled="loading"
            @refresh="handleGenerateQuestionsSuccess"
          />
          <!-- 批量删除分段 -->
          <el-button type="danger" plain :loading="loading" :disabled="loading || !selectedParagraphIds.length" @click="handleBatchDeleteParagraphs">
            删除
          </el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>
  <CreateParagraphDialog
    v-if="createDialogMounted"
    ref="createDialogRef"
    :knowledge-id="knowledgeId"
    :document-id="documentId"
    @success="handleCreateParagraphSuccess"
    @closed="createDialogMounted = false"
  />
  <EditParagraphDialog
    v-if="editDialogMounted"
    ref="editDialogRef"
    title="分段详情"
    :knowledge-id="knowledgeId"
    :document-id="documentId"
    @success="handleReplaceParagraph"
    @closed="editDialogMounted = false"
  />
</template>
