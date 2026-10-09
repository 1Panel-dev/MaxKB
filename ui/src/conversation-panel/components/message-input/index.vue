<script setup lang="ts">
import { ref } from 'vue'
import { getFileExtension, getFileIconUrl, isAudio, isVideo } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'
import { inputShortcut } from '../../core/shortcuts'
import { useMessageInputStore } from './index'

const { question, fileList, maxFiles, maxSizeMB, acceptList, loading, disabled, placeholder, canSend, imageFiles, addFiles, removeFile, send, stop } =
  useMessageInputStore()

// 选择和粘贴附件统一交给输入 Store 处理。
const fileInputRef = ref<HTMLInputElement | null>(null)

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  addFiles(input.files)
  input.value = ''
}

const handlePaste = (event: ClipboardEvent) => {
  const files = event.clipboardData?.files
  if (!files?.length) return
  event.preventDefault()
  addFiles(files)
}

// 移动端保留回车换行，桌面端沿用公共发送快捷键。
const handleKeydown = (event: KeyboardEvent) => {
  const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  if (isMobile && event.key === 'Enter') return
  inputShortcut(event, question, () => {
    if (canSend.value) send()
  })
}
</script>

<template>
  <div class="mk-input-box mk-conversation-message-input w-full shadow-lg">
    <!-- 附件按上传顺序排列，超出可视范围时显示滚动箭头。 -->
    <MkHorizontalScroll v-if="fileList.length" class="mb-3">
      <template v-for="(file, index) in fileList" :key="file.uid">
        <div class="group relative shrink-0">
          <!-- 图片 -->
          <el-image v-if="imageFiles.includes(file)" :src="file.url || file.previewUrl" :alt="file.name" :title="file.name" fit="cover" />
          <!-- 音频 -->
          <MkAudio v-else-if="isAudio(file.name)" :src="file.previewUrl || file.url || ''" :name="file.name">
            <el-card shadow="never" class="small w-60 rounded-lg! cursor-pointer">
              <div class="flex-align-center gap-2">
                <img :src="getFileIconUrl(file.name)" alt="" class="w-8 shrink-0" />
                <div class="min-w-0 flex-1">
                  <div class="truncate" :title="file.name">{{ file.name }}</div>
                  <div class="text-sm text-N500">{{ getFileExtension(file.name) || '文件' }} – {{ formatFileSize(file.size) }}</div>
                </div>
              </div>
            </el-card>
          </MkAudio>
          <!-- 视频 -->
          <MkVideo v-else-if="isVideo(file.name)" :src="file.previewUrl || file.url || ''" :name="file.name">
            <el-card shadow="never" class="small w-60 rounded-lg! cursor-pointer">
              <div class="flex-align-center gap-2">
                <img :src="getFileIconUrl(file.name)" alt="" class="w-8 shrink-0" />
                <div class="min-w-0 flex-1">
                  <div class="truncate" :title="file.name">{{ file.name }}</div>
                  <div class="text-sm text-N500">{{ getFileExtension(file.name) || '文件' }} – {{ formatFileSize(file.size) }}</div>
                </div>
              </div>
            </el-card>
          </MkVideo>
          <!-- 文档 -->
          <el-card v-else shadow="never" class="small w-60 rounded-lg!">
            <div class="flex-align-center gap-2">
              <img :src="getFileIconUrl(file.name)" alt="" class="w-8 shrink-0" />
              <div class="min-w-0 flex-1">
                <div class="truncate" :title="file.name">{{ file.name }}</div>
                <div class="text-sm text-N500">{{ getFileExtension(file.name) || '文件' }} – {{ formatFileSize(file.size) }}</div>
              </div>
            </div>
          </el-card>
          <!-- 上传进度：主题色从左到右填充，上传完成后隐藏 -->
          <div v-if="file.uploading" class="pointer-events-none absolute inset-0 overflow-hidden rounded-lg">
            <div class="h-full bg-primary/15 transition-[width] duration-200" :style="{ width: `${file.progress ?? 0}%` }" />
          </div>
          <!-- 移除附件 -->
          <div class="group-hover-visible attachment-remove" @click="removeFile(index)">
            <MkIcon name="icon_close_bold_outlined" class="text-white!" :size="6" />
          </div>
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
      @paste="handlePaste"
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
        <el-button text :disabled="disabled || loading || fileList.length >= maxFiles" @click="fileInputRef?.click()">
          <MkIcon name="icon_attachment_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
      <el-divider direction="vertical" class="ml-3! mr-4!" />
      <!-- 停止回复 -->
      <el-button v-if="loading" circle type="primary" @click="stop">
        <MkIcon name="icon_square_filled" />
      </el-button>
      <!-- 发送 -->
      <el-button v-else circle type="primary" :disabled="!canSend" @click="send()">
        <MkIcon name="icon_arrow-up_outlined" />
      </el-button>
    </div>
  </div>
</template>
