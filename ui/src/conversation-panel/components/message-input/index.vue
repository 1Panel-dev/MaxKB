<script setup lang="ts">
import { ref } from 'vue'
import { Headset } from '@element-plus/icons-vue'
import { getFileExtension, getFileIconUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'
import { inputShortcut } from '../../core/shortcuts'
import { useMessageInputStore } from './index'

const {
  question,
  fileList,
  maxFiles,
  maxSizeMB,
  acceptList,
  loading,
  placeholder,
  canSend,
  imageFiles,
  audioFiles,
  videoFiles,
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
  <div class="mk-input-box mk-conversation-message-input w-full shadow-lg">
    <!-- 文件预览区域：所有类型按上传顺序横向排列。 // TODO 未来会改成横向有左右按钮控制 -->
    <el-scrollbar v-if="fileList.length" class="mb-3 h-auto!" view-class="flex-align-center gap-2">
      <template v-for="(file, index) in fileList" :key="file.uid">
        <div class="group relative shrink-0">
          <el-image
            v-if="imageFiles.includes(file) && (file.url || file.previewUrl)"
            :src="file.url || file.previewUrl"
            :alt="file.name"
            :title="file.name"
            fit="cover"
          />
          <video v-else-if="videoFiles.includes(file) && file.url" :src="file.url" :title="file.name" controls autoplay class="object-cover" />
          <el-card shadow="never" v-else class="small w-60 rounded-lg!">
            <div class="flex-align-center gap-2">
              <MkIcon v-if="audioFiles.includes(file)" :icon="Headset" :size="24" class="shrink-0 text-N600" />
              <img v-else :src="getFileIconUrl(file.name)" alt="" class="w-8 shrink-0" />
              <div class="min-w-0 flex-1">
                <div class="truncate" :title="file.name">{{ file.name }}</div>
                <div class="text-sm text-N500">{{ getFileExtension(file.name).toUpperCase() || '文件' }} – {{ formatFileSize(file.size) }}</div>
              </div>
            </div>
          </el-card>
          <!-- 移除附件 -->
          <div class="group-hover-visible attachment-remove" @click="removeFile(index)">
            <MkIcon name="icon_close_bold_outlined" class="text-white!" :size="6" />
          </div>
        </div>
      </template>
    </el-scrollbar>

    <!-- 输入框 -->
    <el-input
      v-model="question"
      :autosize="{ minRows: 1, maxRows: 7 }"
      type="textarea"
      resize="none"
      :placeholder="placeholder"
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
        <el-button text :disabled="loading || fileList.length >= maxFiles" @click="fileInputRef?.click()">
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

<style scoped lang="scss"></style>
