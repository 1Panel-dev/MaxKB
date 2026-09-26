<script setup lang="ts">
import { ref } from 'vue'
import { CircleCloseFilled, Paperclip, Promotion, VideoPause } from '@element-plus/icons-vue'
import { inputShortcut } from '../../core/shortcuts'
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
  inputShortcut(e, question, () => {
    if (canSend.value) send()
  })
}
</script>

<template>
  <div class="mk-input-box conversation-message-input w-full border shadow-lg transition-colors focus-within:border-primary">
    <!-- 文件预览区域 -->
    <div v-if="fileList.length" class="mb-3 space-y-2">
      <!-- 图片预览 -->
      <el-space v-if="imageFiles.length" wrap>
        <template v-for="(file, index) in imageFiles" :key="file.uid">
          <div class="relative" @mouseenter="showDelete = file.url || ''" @mouseleave="showDelete = ''">
            <!-- 移除图片附件 -->
            <button
              v-if="showDelete === file.url"
              type="button"
              class="attachment-remove absolute -top-[5px] -right-[5px] z-1"
              @click="removeFile(index)"
            >
              <MkIcon :icon="CircleCloseFilled" />
            </button>
            <el-image v-if="file.url" :src="file.url" fit="cover" class="block h-10 w-10 rounded-md" />
            <el-image v-else-if="file.previewUrl" :src="file.previewUrl" fit="cover" class="block h-10 w-10 rounded-md" />
          </div>
        </template>
      </el-space>

      <!-- 文档预览 -->
      <el-row v-if="documentFiles.length" :gutter="8" class="gap-y-2">
        <template v-for="(file, index) in documentFiles" :key="file.uid">
          <el-col :xs="24" :sm="12">
            <el-card shadow="never" body-class="p-2!" class="cursor-pointer" @mouseenter="showDelete = file.url || ''" @mouseleave="showDelete = ''">
              <div class="flex-between gap-2">
                <div class="flex-align-center min-w-0 gap-1">
                  <img :src="getFileIcon(file.name)" alt="" class="w-6 shrink-0" />
                  <span class="truncate" :title="file.name">{{ file.name }}</span>
                </div>
                <!-- 移除文档附件 -->
                <button v-if="showDelete === file.url" type="button" class="attachment-remove" @click="removeFile(index)">
                  <MkIcon :icon="CircleCloseFilled" />
                </button>
              </div>
            </el-card>
          </el-col>
        </template>
      </el-row>

      <!-- 音频预览 -->
      <el-row v-if="audioFiles.length" :gutter="8" class="gap-y-2">
        <template v-for="(file, index) in audioFiles" :key="file.uid">
          <el-col :xs="24" :sm="12">
            <el-card shadow="never" body-class="p-2!" class="cursor-pointer" @mouseenter="showDelete = file.url || ''" @mouseleave="showDelete = ''">
              <div class="flex-between gap-2">
                <div class="flex-align-center min-w-0 gap-1">
                  <img :src="getFileIcon(file.name)" alt="" class="w-6 shrink-0" />
                  <span class="truncate" :title="file.name">{{ file.name }}</span>
                </div>
                <!-- 移除音频附件 -->
                <button v-if="showDelete === file.url" type="button" class="attachment-remove" @click="removeFile(index)">
                  <MkIcon :icon="CircleCloseFilled" />
                </button>
              </div>
            </el-card>
          </el-col>
        </template>
      </el-row>

      <!-- 视频预览 -->
      <el-space v-if="videoFiles.length" wrap>
        <template v-for="(file, index) in videoFiles" :key="file.uid">
          <div class="relative" @mouseenter="showDelete = file.url || ''" @mouseleave="showDelete = ''">
            <!-- 移除视频附件 -->
            <button
              v-if="showDelete === file.url"
              type="button"
              class="attachment-remove absolute -top-[5px] -right-[5px] z-1"
              @click="removeFile(index)"
            >
              <MkIcon :icon="CircleCloseFilled" />
            </button>
            <video v-if="file.url" :src="file.url" controls class="block w-25 rounded-md" autoplay />
          </div>
        </template>
      </el-space>
    </div>

    <!-- 输入框 -->
    <el-input
      v-model="question"
      :autosize="{ minRows: 1, maxRows: 10 }"
      type="textarea"
      resize="none"
      :placeholder="placeholder"
      :maxlength="100000"
      @keydown.enter="handleKeydown"
      @paste="handlePaste"
      clearable
    />

    <!-- 操作栏 -->
    <div class="mt-2 flex-align-center justify-end">
      <input ref="fileInputRef" type="file" multiple :accept="acceptList" class="hidden" @change="handleFileSelect" />
      <MkTooltip placement="top" popper-class="max-w-75">
        <template #content>
          <div class="break-all whitespace-pre-wrap">支持上传图片、文档、音频、视频文件，最多{{ maxFiles }}个，单个文件最大{{ maxSizeMB }}MB</div>
        </template>
        <!-- 上传文件 -->
        <el-button text :disabled="loading || fileList.length >= maxFiles" @click="fileInputRef?.click()">
          <MkIcon :icon="Paperclip" :size="20" />
        </el-button>
      </MkTooltip>
      <el-divider direction="vertical" />
      <!-- 发送 -->
      <el-button v-if="!loading" text :disabled="!canSend" @click="send">
        <MkIcon :icon="Promotion" :size="20" />
      </el-button>
      <!-- 停止回复 -->
      <el-button v-else text @click="stop">
        <MkIcon :icon="VideoPause" :size="20" />
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
/* 附件删除按钮，供图片、文档、音频和视频预览复用。 */
.attachment-remove {
  align-items: center;
  background: transparent;
  border: 0;
  color: var(--mk-N600);
  cursor: pointer;
  display: flex;
  flex-shrink: 0;
  justify-content: center;
  padding: 0;

  &:hover {
    color: var(--mk-danger);
  }
}
</style>
