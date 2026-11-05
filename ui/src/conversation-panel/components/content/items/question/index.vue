<script setup lang="ts">
import { computed, inject, ref, watch } from 'vue'
import QuestionEditor from './QuestionEditor.vue'
import { useMessageInputStoreOptional } from '../../../message-input/index'
import MkAudio from '@/components/global/mk-media-preview/MkAudio.vue'
import MkVideo from '@/components/global/mk-media-preview/MkVideo.vue'
import FileUploadCard from '@/components/mk-drag-upload/FileUploadCard.vue'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import { getFileExtension, resetUrl } from '@/utils/icon'
import { formatFileSize } from '@/utils/number'
import { downloadByURL } from '@/utils/common'
import { copyText } from '@/utils/clipboard'

import { MESSAGE_LIST_KEY } from '../../../message-list/index'
import { CONVERSATION_LIST_KEY } from '../../../../left-sidebar/conversation-list/index'
import { useViewType } from '../../../../view/index'
import { SHAREABLE_VIEWS, useShareLinkStoreOptional, useShareRecordId } from '../../../message-list/share/index'

defineOptions({ name: 'ConversationQuestionContent' })

// 仅提供分享服务的视图（对话、门户）显示分享入口；进入分享时预先勾选所属轮次。
const showShare = SHAREABLE_VIEWS.includes(useViewType())
const shareLink = useShareLinkStoreOptional()
const shareRecordId = useShareRecordId()

// 复用对话的分享选择入口，回答生成中禁用。
const conversationList = inject(CONVERSATION_LIST_KEY, null)
const messageList = inject(MESSAGE_LIST_KEY, null)
const canShare = computed(() => Boolean(messageList?.messages.value.length && !messageList.streamLoading.value))

interface QuestionAttachment {
  file_id?: string
  name: string
  url?: string
  size?: number
}

type AttachmentField = 'document_list' | 'image_list' | 'audio_list' | 'video_list' | 'other_list'
type QuestionContent = { content?: string } & Partial<Record<AttachmentField, QuestionAttachment[]>>

const props = defineProps<{ content: QuestionContent }>()

// 编辑保留原提问及附件，发送沿用输入框的新问题流程。
const messageInput = useMessageInputStoreOptional()
const editing = ref(false)
const canEdit = computed(() =>
  Boolean(messageInput && !messageInput.disabled.value && !messageInput.streamLoading.value && !conversationList?.isShared.value),
)

function startEditing() {
  if (canEdit.value) editing.value = true
}

function sendEditedQuestion(question: string) {
  if (!canEdit.value || !question.trim()) return
  messageInput?.sendQuestion(question, { attachments: props.content })
}

watch(canEdit, (available) => {
  if (!available) editing.value = false
})

// 非图片附件统一排列在上方，图片单独放在下方。
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
const attachmentGroups = computed(() =>
  [
    { type: 'file', files: attachments.value.filter((file) => file.field !== 'image_list') },
    { type: 'image', files: attachments.value.filter((file) => file.field === 'image_list') },
  ].filter((group) => group.files.length > 0),
)
const imageSources = computed(() => attachments.value.filter((file) => file.field === 'image_list' && file.src).map((file) => file.src))

function getAttachmentDescription(file: QuestionAttachment) {
  const extension = getFileExtension(file.name) || '文件'
  return file.size == null ? extension : `${extension} – ${formatFileSize(file.size)}`
}
</script>

<template>
  <div
    class="mk-conversation-question-content group/question space-y-3"
    :class="editing ? 'question-editor border border-primary rounded-2xl p-3' : 'cursor-pointer'"
  >
    <!-- 视频、音频和文档共用一行，图片在下方；超出当前宽度时自动换行。 -->
    <div v-if="attachments.length" class="max-w-full space-y-2">
      <template v-for="attachmentGroup in attachmentGroups" :key="attachmentGroup.type">
        <div class="flex max-w-full flex-wrap justify-end gap-2">
          <template v-for="file in attachmentGroup.files" :key="file.key">
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
      </template>
    </div>
    <QuestionEditor v-if="editing" :content="content.content ?? ''" :disabled="!canEdit" @cancel="editing = false" @send="sendEditedQuestion" />
    <div v-else-if="content.content" class="mk-gray-card-lg ml-auto w-fit max-w-full py-3! whitespace-pre-wrap wrap-anywhere">
      {{ content.content }}
    </div>
    <div
      v-if="!editing"
      class="h-8 -mt-3 flex items-center justify-end gap-1 invisible group-hover/question:visible group-focus-within/question:visible"
    >
      <!-- 编辑提问 -->
      <MkTooltip v-if="messageInput" content="编辑">
        <el-button text :disabled="!canEdit" @click="startEditing">
          <MkIcon name="icon_edit_outlined" />
        </el-button>
      </MkTooltip>
      <!-- 复制提问 -->
      <el-button text @click="copyText(content.content)">
        <MkIcon name="icon_copy_outlined" />
      </el-button>
      <!-- 进入分享模式 -->
      <MkTooltip v-if="showShare" content="分享">
        <el-button text :disabled="!canShare" @click="shareLink?.enterShare([shareRecordId])">
          <MkIcon name="icon_share_outlined" />
        </el-button>
      </MkTooltip>
    </div>
  </div>
</template>

<style scoped lang="scss">
.question-editor {
  width: 100%;
}
</style>
