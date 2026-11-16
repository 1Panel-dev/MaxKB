<script setup lang="ts">
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import { useInputEvents } from '../../core/input-events'
import FileCard from './file-card/index.vue'
import { useMessageInputStore } from './index'
import UrlUpload from './url-upload/index.vue'
import UserForm from './user-form/index.vue'
import { useVoiceRecorder } from './voice-recorder/index'
import VoiceRecorder from './voice-recorder/index.vue'
import { isAudio, isVideo } from '@/utils/icon'

const {
  question,
  fileList,
  uploadEnabled,
  urlUploadEnabled,
  canUpload,
  maxFiles,
  maxSizeMB,
  allowedExtensions,
  acceptList,
  streamLoading,
  disabled,
  placeholder,
  canSend,
  speechEnabled,
  transcribing,
  transcribe,
  imageFiles,
  addFiles,
  removeFile,
  send,
  stop,
} = useMessageInputStore()

// 所有附件入口共用禁用条件，上传和发送仍由输入 Store 处理。
const { fileInputRef, handlePaste, handleDragover, handleDrop, handleKeydown } = useInputEvents({
  text: question,
  canUpload: () => canUpload.value && uploadEnabled.value,
  addFiles,
  submit: () => {
    if (canSend.value) send()
  },
})

// 本地选择仅通过明确的上传按钮进入。
function handleLocalSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (uploadEnabled.value && canUpload.value) addFiles(input.files)
  input.value = ''
}

// 语音输入：点击麦克风开始录音，点击停止后转写到输入框
const { recording, seconds: recordSeconds, waveLevels, start: startRecording, stop: stopRecording } = useVoiceRecorder(transcribe)
</script>

<template>
  <!-- 录音中 -->
  <VoiceRecorder v-if="recording" :seconds="recordSeconds" :wave-levels="waveLevels" @stop="stopRecording" />
  <div v-else class="mk-input-box mk-conversation-message-input w-full shadow-lg" @dragover="handleDragover" @drop="handleDrop" @paste="handlePaste">
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
            :show-error="false"
            @remove="removeFile(index)"
          />
          <!-- 音频 -->
          <MkAudio v-else-if="isAudio(file.name)" :src="file.previewUrl || file.url || ''" :name="file.name">
            <FileCard :file="file" :percentage="file.progress" class="w-60 cursor-pointer rounded-lg!" @remove="removeFile(index)" />
          </MkAudio>
          <!-- 视频 -->
          <MkVideo v-else-if="isVideo(file.name)" :src="file.previewUrl || file.url || ''" :name="file.name">
            <FileCard :file="file" :percentage="file.progress" class="w-60 cursor-pointer rounded-lg!" @remove="removeFile(index)" />
          </MkVideo>
          <!-- 文档 -->
          <FileCard
            v-else
            :file="file"
            :percentage="file.progress"
            :disabled="disabled || streamLoading"
            class="w-60 cursor-pointer rounded-lg!"
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
    <div class="mt-3 flex items-center">
      <!-- 用户输入参数表单 -->
      <UserForm class="mr-3" />
      <!-- 本地文件选择：供直接上传按钮和 URL 浮层的本地上传入口共用 -->
      <input v-if="uploadEnabled" ref="fileInputRef" type="file" multiple :accept="acceptList" class="hidden" @change="handleLocalSelect" />
      <!-- 仅本地上传模式：展示拖拽提示，点击附件按钮直接选择文件 -->
      <MkTooltip v-if="uploadEnabled && !urlUploadEnabled" placement="top">
        <template #content>
          <div class="break-all whitespace-pre-wrap">
            可拖拽到输入框内上传文件
            <br />
            上传文件：最多{{ maxFiles }}个，每个文件限制{{ maxSizeMB }}MB
            <br />
            文件类型：{{ allowedExtensions.join('、') }}
          </div>
        </template>
        <el-button text :disabled="!canUpload" @click="fileInputRef?.click()">
          <MkIcon name="icon_attachment_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
      <!-- URL 上传模式：附件按钮打开浮层，本地上传事件触发文件选择 -->
      <UrlUpload v-if="urlUploadEnabled" @local-upload="fileInputRef?.click()" />
      <!-- 语音输入：点击开始录音 -->
      <el-button
        v-if="speechEnabled"
        text
        class="ml-2!"
        :loading="transcribing"
        :disabled="disabled || streamLoading || transcribing"
        @click="startRecording"
      >
        <MkIcon v-if="!transcribing" name="icon_mic_outlined" :size="18" class="text-N900!" />
      </el-button>
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
