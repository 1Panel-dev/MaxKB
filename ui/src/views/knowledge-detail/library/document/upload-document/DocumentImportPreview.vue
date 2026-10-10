<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { DocumentImportParagraph, DocumentSplitResult } from '@/api/types'
import { getFileIconUrl } from '@/utils/icon'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'DocumentImportPreview' })
const documents = defineModel<DocumentSplitResult[]>({ required: true })
const selectedDocumentIndex = ref(0)
const selectedDocument = computed(() => documents.value[selectedDocumentIndex.value])
const editingParagraphIndex = ref<number>()
const paragraphDraft = ref<DocumentImportParagraph>({ title: '', content: '' })

/* 预览文档选择与分段草稿编辑 */
function handleSelectDocument(index: number) {
  selectedDocumentIndex.value = index
  editingParagraphIndex.value = undefined
}

function handleEditParagraph(index: number) {
  const paragraph = selectedDocument.value?.content[index]
  if (!paragraph) return
  paragraphDraft.value = cloneDeep(paragraph)
  editingParagraphIndex.value = index
}

function handleSaveParagraph() {
  if (!paragraphDraft.value.content.trim()) {
    MsgWarning('分段内容不能为空')
    return
  }
  const index = editingParagraphIndex.value
  if (index === undefined || !selectedDocument.value) return
  selectedDocument.value.content[index] = cloneDeep(paragraphDraft.value)
  editingParagraphIndex.value = undefined
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
  editingParagraphIndex.value = undefined
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
                <img :src="getFileIconUrl(document.name)" alt="" class="size-6 shrink-0" />
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
            <el-card shadow="never" class="group" body-class="relative">
              <el-form v-if="editingParagraphIndex === index" label-position="top" @submit.prevent>
                <el-form-item label="标题">
                  <el-input v-model="paragraphDraft.title" maxlength="256" placeholder="请输入标题" />
                </el-form-item>
                <el-form-item label="内容" required>
                  <el-input v-model="paragraphDraft.content" type="textarea" :rows="6" placeholder="请输入分段内容" />
                </el-form-item>
                <div class="flex justify-end gap-2">
                  <!-- 取消分段编辑 -->
                  <el-button @click="editingParagraphIndex = undefined">取消</el-button>
                  <!-- 保存分段编辑 -->
                  <el-button type="primary" @click="handleSaveParagraph">保存</el-button>
                </div>
              </el-form>
              <template v-else>
                <div class="group-hover-visible absolute top-3 right-3 flex rounded-lg bg-white shadow-sm">
                  <!-- 编辑预览分段 -->
                  <el-button text title="编辑分段" @click="handleEditParagraph(index)"><MkIcon name="icon_edit_outlined" /></el-button>
                  <!-- 删除预览分段 -->
                  <el-button class="ml-0!" text title="删除分段" @click="handleDeleteParagraph(index)">
                    <MkIcon name="icon_delete-trash_outlined" />
                  </el-button>
                </div>
                <h4 v-if="paragraph.title" class="mb-3 pr-20">{{ index + 1 }}、{{ paragraph.title }}</h4>
                <MdPreview :model-value="paragraph.content" />
                <p class="mt-3 text-sm text-N600">{{ paragraph.content.length }} 字符</p>
              </template>
            </el-card>
          </template>
        </div>
        <MkEmpty v-if="!selectedDocument.content.length" description="暂无分段" />
      </template>
      <MkEmpty v-else description="暂无预览文档" />
    </template>
  </MkViewLayout>
</template>
