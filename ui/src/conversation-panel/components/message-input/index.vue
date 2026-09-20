<template>
  <div class="operate-textarea">
    <!-- 文件预览区域 -->
    <div v-if="fileList.length" class="file-preview-list">
      <!-- 图片预览 -->
      <el-space wrap>
        <template v-for="(f, i) in imageFiles" :key="f.uid">
          <div class="file-item file-image" @mouseenter="showDelete = f.url || ''" @mouseleave="showDelete = ''">
            <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
              <el-icon style="font-size: 16px; top: 2px"><CircleCloseFilled /></el-icon>
            </div>
            <el-image v-if="f.url" :src="f.url" fit="cover" style="width: 40px; height: 40px; display: block" class="border-r-6" />
            <el-image v-else-if="f.previewUrl" :src="f.previewUrl" fit="cover" style="width: 40px; height: 40px; display: block" class="border-r-6" />
          </div>
        </template>
      </el-space>

      <!-- 文档预览 -->
      <el-row :gutter="10">
        <el-col v-for="(f, i) in documentFiles" :key="f.uid" :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb-8">
          <el-card shadow="never" style="--el-card-padding: 8px; max-width: 100%" class="file-card">
            <div class="flex-between align-center" @mouseenter="showDelete = f.url || ''" @mouseleave="showDelete = ''">
              <div class="flex align-center">
                <img :src="getFileIcon(f.name)" alt="" width="24" />
                <div class="ml-4 ellipsis-1" :title="f.name">{{ f.name }}</div>
              </div>
              <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
                <el-icon style="font-size: 16px; top: 2px"><CircleCloseFilled /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 音频预览 -->
      <el-row :gutter="10">
        <el-col v-for="(f, i) in audioFiles" :key="f.uid" :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb-8">
          <el-card shadow="never" style="--el-card-padding: 8px" class="file-card">
            <div class="flex-between align-center" @mouseenter="showDelete = f.url || ''" @mouseleave="showDelete = ''">
              <div class="flex align-center">
                <img :src="getFileIcon(f.name)" alt="" width="24" />
                <div class="ml-4 ellipsis-1" :title="f.name">{{ f.name }}</div>
              </div>
              <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
                <el-icon style="font-size: 16px; top: 2px"><CircleCloseFilled /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 视频预览 -->
      <el-space wrap>
        <template v-for="(f, i) in videoFiles" :key="f.uid">
          <div class="file-item file-image" @mouseenter="showDelete = f.url || ''" @mouseleave="showDelete = ''">
            <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
              <el-icon style="font-size: 16px; top: 2px"><CircleCloseFilled /></el-icon>
            </div>
            <video v-if="f.url" :src="f.url" controls style="width: 100px; display: block" class="border-r-6" autoplay />
          </div>
        </template>
      </el-space>
    </div>

    <!-- 输入框 -->
    <el-input
      ref="inputRef"
      v-model="question"
      :autosize="{ minRows: 1, maxRows: 10 }"
      type="textarea"
      :placeholder="placeholder"
      :maxlength="100000"
      @keydown.enter="handleKeydown"
      @paste="handlePaste"
      class="chat-operate-textarea"
      clearable
    />

    <!-- 操作栏 -->
    <div class="operate flex-between">
      <div></div>
      <div class="flex align-center">
        <input ref="fileInputRef" type="file" multiple :accept="acceptList" style="display: none" @change="handleFileSelect" />
        <el-tooltip effect="dark" placement="top" popper-class="upload-tooltip-width">
          <template #content>
            <div class="break-all pre-wrap">支持上传图片、文档、音频、视频文件，最多{{ maxFiles }}个，单个文件最大{{ maxSizeMB }}MB</div>
          </template>
          <!-- 上传文件 -->
          <el-button text :disabled="loading || fileList.length >= maxFiles" @click="fileInputRef?.click()">
            <el-icon :size="20"><Paperclip /></el-icon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <!-- 发送 -->
        <el-button v-if="!loading" text class="sent-button" :disabled="!canSend" @click="send">
          <el-icon :size="20"><Promotion /></el-icon>
        </el-button>
        <!-- 停止回复 -->
        <el-button v-else text class="sent-button stop-button" @click="stop">
          <el-icon :size="20"><VideoPause /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { CircleCloseFilled, Paperclip, Promotion, VideoPause } from '@element-plus/icons-vue'
import { useMessageInputStore } from './index'

const {
  question,
  fileList,
  showDelete,
  maxFiles,
  maxSizeMB,
  acceptList,
  loading,
  placeholder,
  canSend,
  imageFiles,
  documentFiles,
  audioFiles,
  videoFiles,
  getFileIcon,
  addFiles,
  removeFile,
  send,
  stop,
} = useMessageInputStore()

const inputRef = ref<any>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  addFiles(input.files)
  input.value = ''
}

const handlePaste = (e: ClipboardEvent) => {
  const files = e.clipboardData?.files
  if (!files?.length) return
  e.preventDefault()
  addFiles(files)
}

const handleKeydown = (e: KeyboardEvent) => {
  const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  if (isMobile && e.key === 'Enter') return
  if (!e.ctrlKey && !e.shiftKey && !e.altKey && !e.metaKey) {
    e.preventDefault()
    if (canSend.value && !e.isComposing) send()
  } else {
    const textarea = inputRef.value?.$el?.querySelector('.el-textarea__inner') as HTMLTextAreaElement
    if (textarea) {
      const startPos = textarea.selectionStart
      const endPos = textarea.selectionEnd
      e.preventDefault()
      question.value = question.value.slice(0, startPos) + '\n' + question.value.slice(endPos)
      nextTick(() => textarea.setSelectionRange(startPos + 1, startPos + 1))
    }
  }
}
</script>

<style scoped lang="scss">
.operate-textarea {
  width: 100%;
  max-width: 680px;
  box-shadow: 0px 6px 24px 0px rgba(var(--el-text-color-primary-rgb), 0.08);
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #ffffff;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.operate-textarea:focus-within {
  border: 1px solid var(--el-color-primary);
}
.operate-textarea :deep(.el-textarea__inner) {
  border-radius: 8px !important;
  box-shadow: none;
  resize: none;
  padding: 13px 16px;
  box-sizing: border-box;
  min-height: 47px !important;
}
.file-preview-list {
  padding: 8px 12px;
}
.file-item {
  position: relative;
  overflow: inherit;
}
.file-image .delete-icon {
  position: absolute;
  right: -5px;
  top: -5px;
  z-index: 1;
}
.delete-icon {
  cursor: pointer;
  color: var(--el-color-info);
}
.delete-icon:hover {
  color: var(--el-color-danger);
}
.file-card {
  cursor: pointer;
}
.operate {
  padding: 6px 10px;
}
.sent-button {
  max-height: none;
}
.stop-button {
  cursor: pointer !important;
}
.stop-button:hover {
  color: var(--el-color-danger);
}
.sent-button .el-icon {
  font-size: 24px;
}
.mb-8 {
  margin-bottom: 8px;
}
.flex-between {
  display: flex;
  justify-content: space-between;
}
.align-center {
  align-items: center;
}
.flex {
  display: flex;
}
.ellipsis-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.border-r-6 {
  border-radius: 6px;
}
.break-all {
  word-break: break-all;
}
.pre-wrap {
  white-space: pre-wrap;
}
.ml-4 {
  margin-left: 4px;
}
.upload-tooltip-width {
  width: 300px;
}
</style>
