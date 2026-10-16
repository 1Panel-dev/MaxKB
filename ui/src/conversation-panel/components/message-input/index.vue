<script setup lang="ts">
import { getFileExtension, isAudio, isVideo } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'
import { useInputEvents } from '../../core/input-events'
import { useMessageInputStore, type FileItem } from './index'
import FileUploadCard from '@/components/mk-drag-upload/FileUploadCard.vue'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'

const {
  question,
  fileList,
  maxFiles,
  maxSizeMB,
  acceptList,
  streamLoading,
  disabled,
  placeholder,
  canSend,
  imageFiles,
  addFiles,
  removeFile,
  retryFile,
  send,
  stop,
} = useMessageInputStore()

// 所有附件入口共用禁用条件，上传和发送仍由输入 Store 处理。
const { fileInputRef, handleFileSelect, handlePaste, handleDragover, handleDrop, handleKeydown } = useInputEvents({
  text: question,
  canUpload: () => !disabled.value && !streamLoading.value && fileList.value.length < maxFiles,
  addFiles,
  submit: () => {
    if (canSend.value) send()
  },
})
// 对话附件保留类型与已上传大小文案，卡片负责统一展示。
function getAttachmentDescription(file: FileItem) {
  const uploaded = file.status === 'uploading' ? formatFileSize((file.size * (file.progress ?? 0)) / 100) + ' / ' : ''
  return (getFileExtension(file.name) || '文件') + ' – ' + uploaded + formatFileSize(file.size)
}
</script>

<template>
  <div class="mk-input-box mk-conversation-message-input w-full shadow-lg" @dragover="handleDragover" @drop="handleDrop" @paste="handlePaste">
    <!-- 附件按上传顺序排列，超出可视范围时显示滚动箭头。 -->
    <MkHorizontalScroll v-if="fileList.length" class="mb-3">
      <template v-for="(file, index) in fileList" :key="file.uid">
        <div class="group relative shrink-0">
          <!-- 图片 -->
          <ImageUploadCard
            v-if="imageFiles.includes(file)"
            :file="file"
            :src="file.url || file.previewUrl"
            :size="58"
            :percentage="file.progress"
            :disabled="disabled || streamLoading"
            :show-error="false"
            @retry="retryFile(file)"
            @remove="removeFile(index)"
          />
          <!-- 音频 -->
          <MkAudio v-else-if="isAudio(file.name)" :src="file.previewUrl || file.url || ''" :name="file.name">
            <FileUploadCard
              :file="file"
              :description="getAttachmentDescription(file)"
              :percentage="file.progress"
              :disabled="disabled || streamLoading"
              class="w-60 cursor-pointer rounded-lg!"
              @retry="retryFile(file)"
              @remove="removeFile(index)"
            />
          </MkAudio>
          <!-- 视频 -->
          <MkVideo v-else-if="isVideo(file.name)" :src="file.previewUrl || file.url || ''" :name="file.name">
            <FileUploadCard
              :file="file"
              :description="getAttachmentDescription(file)"
              :percentage="file.progress"
              :disabled="disabled || streamLoading"
              class="w-60 cursor-pointer rounded-lg!"
              @retry="retryFile(file)"
              @remove="removeFile(index)"
            />
          </MkVideo>
          <!-- 文档 -->
          <FileUploadCard
            v-else
            :file="file"
            :description="getAttachmentDescription(file)"
            :percentage="file.progress"
            :disabled="disabled || streamLoading"
            class="w-60 rounded-lg!"
            @retry="retryFile(file)"
            @remove="removeFile(index)"
          />
        </div>
      </template>
    </MkHorizontalScroll>

    <!-- 输入框 -->
    <el-input
      v-model="question"
      :autosize="{ minRows: 1, maxRows: 7 }"
      type="textarea"
      resize="none"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="100000"
      @keydown.enter="handleKeydown"
      clearable
    />

    <!-- 操作栏 -->
    <div class="text-right mt-3">
      <input ref="fileInputRef" type="file" multiple :accept="acceptList" class="hidden" @change="handleFileSelect" />
      <MkTooltip placement="top">
        <template #content>
          <div class="break-all whitespace-pre-wrap">
            可拖拽到输入框内上传文件
            <br />
            上传文件：最多{{ maxFiles }}个，每个文件限制{{ maxSizeMB }}MB
            <br />
            <!-- // TODO: 类型格式处理 -->
            文件类型：{{ acceptList }}
          </div>
        </template>
        <!-- 上传文件 -->
        <el-button text :disabled="disabled || streamLoading || fileList.length >= maxFiles" @click="fileInputRef?.click()">
          <MkIcon name="icon_attachment_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
      <el-divider direction="vertical" class="ml-3! mr-4!" />
      <!-- 停止回复 -->
      <el-button v-if="streamLoading" circle type="primary" @click="stop">
        <MkIcon name="icon_square_filled" />
      </el-button>
      <!-- 发送 -->
      <el-button v-else circle type="primary" :disabled="!canSend" @click="send()">
        <MkIcon name="icon_arrow-up_outlined" />
      </el-button>
    </div>
  </div>
</template>
