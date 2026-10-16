<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import type { DocumentImportParagraph, DocumentSplitResult } from '@/api/types'
import { getFileIconUrl } from '@/utils/icon'
import { getFileUrl } from '@/utils/common'
import { MsgWarning } from '@/utils/message'
import EditParagraphDialog from '../upload-document/EditParagraphDialog.vue'

defineOptions({ name: 'DocumentImportPreview' })
defineProps<{ knowledgeId: string }>()
const documents = defineModel<DocumentSplitResult[]>({ required: true })
const selectedDocumentIndex = ref(0)
const selectedDocument = computed(() => documents.value[selectedDocumentIndex.value])
const editingParagraphIndex = ref<number>()
const editingDocument = ref<DocumentSplitResult>()
const editDialogMounted = ref(false)
const editDialogRef = ref<InstanceType<typeof EditParagraphDialog>>()

/* 预览文档选择与分段草稿编辑 */
function handleSelectDocument(index: number) {
  selectedDocumentIndex.value = index
}

async function handleEditParagraph(index: number) {
  const paragraph = selectedDocument.value?.content[index]
  if (!paragraph) return
  editingDocument.value = selectedDocument.value
  editingParagraphIndex.value = index
  editDialogMounted.value = true
  await nextTick()
  editDialogRef.value?.open(paragraph)
}

function handleSaveParagraph(paragraph: DocumentImportParagraph) {
  const index = editingParagraphIndex.value
  if (index === undefined || !editingDocument.value) return
  editingDocument.value.content[index] = paragraph
}

function handleEditDialogClosed() {
  editDialogMounted.value = false
  editingParagraphIndex.value = undefined
  editingDocument.value = undefined
}

function validate() {
  if (editingParagraphIndex.value !== undefined) {
    MsgWarning('请先保存或取消分段编辑')
    return false
  }
  return true
}

defineExpose({ validate })

function handleDeleteParagraph(index: number) {
  selectedDocument.value?.content.splice(index, 1)
}
</script>

<template>
  <MkViewLayout title="">
    <template #aside="{ Header }">
      <component :is="Header"><h4 class="mk-title-decoration">预览</h4></component>
      <el-scrollbar class="min-h-0 flex-1" view-class="px-4 pb-4">
        <div class="space-y-3">
          <template v-for="(document, index) in documents" :key="index">
            <!-- 切换预览文档 -->
            <el-card
              class="small cursor-pointer hover:border-primary!"
              shadow="never"
              :class="{ 'border-primary! bg-primary/10!': selectedDocumentIndex === index }"
              @click="handleSelectDocument(index)"
              @keydown.enter="handleSelectDocument(index)"
            >
              <div class="flex-align-center gap-2">
                <el-image
                  v-if="document.source_file_id"
                  class="size-8 shrink-0"
                  :src="getFileUrl(document.source_file_id)"
                  :alt="document.name"
                  fit="cover"
                />
                <img v-else :src="getFileIconUrl(document.name)" alt="" class="size-6 shrink-0" />
                <span class="truncate" :title="document.name">{{ document.name }}</span>
              </div>
            </el-card>
          </template>
        </div>
      </el-scrollbar>
    </template>
    <template #default="{ Header }">
      <component :is="Header">
        <p class="text-N600">{{ selectedDocument?.content.length ?? 0 }} 分段</p>
      </component>
      <template v-if="selectedDocument">
        <div class="space-y-3">
          <template v-for="(paragraph, index) in selectedDocument.content" :key="index">
            <el-card shadow="never" class="mk-paragraph-card group overflow-visible!" body-class="overflow-visible!">
              <div class="group-hover-visible sticky top-3 z-10 h-0" @click.stop>
                <el-card class="absolute top-0 right-0" shadow="always" style="--el-card-padding: 4px">
                  <!-- 编辑预览分段 -->
                  <el-button text @click="handleEditParagraph(index)"><MkIcon name="icon_edit_outlined" /></el-button>
                  <!-- 删除预览分段 -->
                  <el-button text @click="handleDeleteParagraph(index)">
                    <MkIcon name="icon_delete-trash_outlined" />
                  </el-button>
                </el-card>
              </div>

              <!-- 图片-->
              <el-image
                v-if="selectedDocument.source_file_id"
                class="w-fit [&_img]:size-auto! [&_img]:max-h-50 mb-2"
                :src="getFileUrl(selectedDocument.source_file_id)"
                :alt="selectedDocument.name"
                fit="contain"
              />

              <h4 v-if="paragraph.title" class="mb-2 pr-20">{{ paragraph.title }}</h4>
              <MdPreview :model-value="paragraph.content" />
              <p class="mt-2 text-sm text-N600">{{ paragraph.content.length }} 字符</p>
            </el-card>
          </template>
        </div>
        <MkEmpty v-if="!selectedDocument.content.length" description="暂无分段" />
      </template>
      <MkEmpty v-else description="暂无预览文档" />
    </template>
  </MkViewLayout>
  <EditParagraphDialog
    v-if="editDialogMounted"
    ref="editDialogRef"
    :knowledge-id="knowledgeId"
    @submit="handleSaveParagraph"
    @closed="handleEditDialogClosed"
  />
</template>
