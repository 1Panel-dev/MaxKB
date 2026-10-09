<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import UploadDocumentDrawer from './UploadDocumentDrawer.vue'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentUploadMode } from './constants'

defineOptions({ name: 'ButtonUploadDocument' })
defineProps<{ api: typeof DocumentApi; knowledgeId: string; fileCountLimit?: number; fileSizeLimit?: number }>()
const emit = defineEmits<{ refresh: [] }>()

/* 上传入口与抽屉生命周期 */
const uploadMode = ref<DocumentUploadMode>()
const drawerRef = useTemplateRef<InstanceType<typeof UploadDocumentDrawer>>('drawerRef')
function handleOpenUpload(mode: DocumentUploadMode) {
  uploadMode.value = mode
  nextTick(() => drawerRef.value?.open())
}
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-end">
    <!-- 上传文档 -->
    <el-button type="primary">
      <span class="mr-1">上传文档</span>
      <MkIcon name="icon_down_outlined" :size="14" />
    </el-button>
    <template #dropdown>
      <MkDropdownMenu class="w-60!">
        <!-- 上传文本文件 -->
        <MkDropdownItem class="py-2!" @click="handleOpenUpload('text')">
          <template #icon><img src="@/assets/file-type/file-document-icon.svg" alt="" class="size-6" /></template>
          <span>文本文件</span>
        </MkDropdownItem>
        <!-- 上传表格 -->
        <MkDropdownItem class="py-2!" @click="handleOpenUpload('table')">
          <template #icon><img src="@/assets/file-type/file-table-icon.svg" alt="" class="size-6" /></template>
          <span>表格</span>
        </MkDropdownItem>
        <!-- 上传 QA 问答对 -->
        <MkDropdownItem class="py-2!" @click="handleOpenUpload('qa')">
          <template #icon><img src="@/assets/file-type/file-qa-icon.svg" alt="" class="size-6" /></template>
          <span>QA 问答对</span>
        </MkDropdownItem>
      </MkDropdownMenu>
    </template>
  </MkDropdown>
  <UploadDocumentDrawer
    v-if="uploadMode"
    ref="drawerRef"
    :api="api"
    :mode="uploadMode"
    :knowledge-id="knowledgeId"
    :file-count-limit="fileCountLimit"
    :file-size-limit="fileSizeLimit"
    @refresh="emit('refresh')"
    @closed="uploadMode = undefined"
  />
</template>
