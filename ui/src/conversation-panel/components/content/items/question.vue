<script setup lang="ts">
import { computed } from 'vue'
import MkAudio from '@/components/global/mk-media-preview/MkAudio.vue'
import MkVideo from '@/components/global/mk-media-preview/MkVideo.vue'
import FileUploadCard from '@/components/mk-drag-upload/FileUploadCard.vue'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import { getFileExtension, resetUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'
import { downloadByURL } from '@/utils/common'

defineOptions({ name: 'ConversationQuestionContent' })

interface QuestionAttachment {
  file_id?: string
  name: string
  url?: string
  size?: number
}

type AttachmentField = 'document_list' | 'image_list' | 'audio_list' | 'video_list' | 'other_list'
type QuestionContent = { content?: string } & Partial<Record<AttachmentField, QuestionAttachment[]>>

const props = defineProps<{ content: QuestionContent }>()

// 合并各类已发送附件，统一换行排列；不依赖输入区的上传状态。
const attachmentFields = ['document_list', 'image_list', 'audio_list', 'video_list', 'other_list'] as const
const attachments = computed(() =>
  attachmentFields.flatMap((field) =>
    (props.content[field] ?? []).map((file, index) => ({
      ...file,
      status: 'success' as const,
      key: `${field}-${file.file_id ?? index}`,
      field,
      src: file.url ? resetUrl(file.url) : '',
    })),
  ),
)
const imageSources = computed(() => attachments.value.filter((file) => file.field === 'image_list' && file.src).map((file) => file.src))

function getAttachmentDescription(file: QuestionAttachment) {
  const extension = getFileExtension(file.name) || '文件'
  return file.size == null ? extension : `${extension} – ${formatFileSize(file.size)}`
}
</script>

<template>
  <div class="mk-conversation-question-content space-y-3">
    <!-- 查看已发送附件，超出当前宽度时自动换行。 -->
    <div v-if="attachments.length" class="flex max-w-full flex-wrap items-start justify-end gap-2">
      <template v-for="file in attachments" :key="file.key">
        <div :class="file.field === 'image_list' ? 'shrink-0' : 'w-60 max-w-full'">
          <!-- 查看图片 -->
          <ImageUploadCard
            v-if="file.field === 'image_list' && file.src"
            :file="file"
            :src="file.src"
            :size="58"
            :show-remove="false"
            :preview-src-list="imageSources"
            :initial-index="imageSources.indexOf(file.src)"
            class="cursor-pointer"
          />
          <!-- 播放音频 -->
          <MkAudio v-else-if="file.field === 'audio_list'" :src="file.src" :name="file.name">
            <FileUploadCard :file="file" :description="getAttachmentDescription(file)" :show-remove="false" class="cursor-pointer rounded-lg!" />
          </MkAudio>
          <!-- 播放视频 -->
          <MkVideo v-else-if="file.field === 'video_list'" :src="file.src" :name="file.name">
            <FileUploadCard :file="file" :description="getAttachmentDescription(file)" :show-remove="false" class="cursor-pointer rounded-lg!" />
          </MkVideo>
          <!-- 下载文件 -->
          <FileUploadCard
            v-else-if="file.field !== 'image_list'"
            :file="file"
            :description="getAttachmentDescription(file)"
            :show-remove="false"
            class="cursor-pointer rounded-lg!"
            @click="file.src && downloadByURL(file.src, file.name)"
          />
        </div>
      </template>
    </div>
    <div v-if="content.content" class="mk-gray-card-lg ml-auto w-fit max-w-full py-3! whitespace-pre-wrap wrap-anywhere">{{ content.content }}</div>
  </div>
</template>
