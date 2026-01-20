<template>
  <!-- 问题内容 -->
  <div @mouseenter.stop="showIcon = true" @mouseleave.stop="showIcon = false">
    <div class="question-content item-content lighter">
      <div v-if="!isReQuestion" class="content p-12-16 border-r-8" :class="getClassName">
        <div class="text break-all pre-wrap">
          <div class="mb-8" v-if="document_list.length">
            <el-space wrap class="w-full media-file-width">
              <template v-for="(item, index) in document_list" :key="index">
                <el-card shadow="never" style="--el-card-padding: 8px" class="download-file cursor">
                  <div class="download-button flex align-center" @click="downloadFile(item)">
                    <el-icon class="mr-4">
                      <Download />
                    </el-icon>
                    {{ $t('chat.download') }}
                  </div>
                  <div class="show flex align-center">
                    <img :src="getImgUrl(item && item?.name)" alt="" width="24" />
                    <div class="ml-4 ellipsis-1" :title="item && item?.name">
                      {{ item && item?.name }}
                    </div>
                  </div>
                </el-card>
              </template>
            </el-space>
          </div>
          <div class="mb-8" v-if="image_list.length">
            <el-space wrap>
              <template v-for="(item, index) in image_list" :key="index">
                <div class="file cursor border-r-6" v-if="item.url">
                  <el-image
                    :src="item.url"
                    :zoom-rate="1.2"
                    :max-scale="7"
                    :min-scale="0.2"
                    :preview-src-list="getAttrsArray(image_list, 'url')"
                    :initial-index="index"
                    alt=""
                    fit="cover"
                    style="width: 170px; height: 170px; display: block"
                    class="border-r-6"
                  />
                </div>
              </template>
            </el-space>
          </div>
          <div class="mb-8" v-if="audio_list.length">
            <el-space wrap>
              <template v-for="(item, index) in audio_list" :key="index">
                <div class="file cursor border-r-6" v-if="item.url">
                  <audio
                    :src="item.url"
                    controls
                    style="width: 350px; height: 43px"
                    class="border-r-6"
                  />
                </div>
              </template>
            </el-space>
          </div>
          <div class="mb-8" v-if="video_list.length">
            <el-space wrap>
              <template v-for="(item, index) in video_list" :key="index">
                <div class="file cursor border-r-6" v-if="item.url">
                  <video
                    :src="item.url"
                    style="width: 170px; display: block"
                    class="border-r-6"
                    controls
                    autoplay
                  />
                </div>
              </template>
            </el-space>
          </div>
          <div class="mb-8" v-if="other_list.length">
            <el-space wrap class="w-full media-file-width">
              <template v-for="(item, index) in other_list" :key="index">
                <el-card shadow="never" style="--el-card-padding: 8px" class="download-file cursor">
                  <div class="download-button flex align-center" @click="downloadFile(item)">
                    <el-icon class="mr-4">
                      <Download/>
                    </el-icon>
                    {{ $t('chat.download') }}
                  </div>
                  <div class="show flex align-center">
                    <img :src="getImgUrl(item && item?.name)" alt="" width="24"/>
                    <div class="ml-4 ellipsis-1" :title="item && item?.name">
                      {{ item && item?.name }}
                    </div>
                  </div>
                </el-card>
              </template>
            </el-space>
          </div>
          <span> {{ chatRecord.problem_text }}</span>
        </div>
      </div>
      <div class="question-content__operate" v-else>
        <div class="operate-textarea">
          <el-input
            ref="quickInputRef"
            v-model="editText"
            :autosize="{ minRows: 1, maxRows: 10 }"
            type="textarea"
            :placeholder="$t('chat.inputPlaceholder.default')"
            :maxlength="100000"
            @keydown.enter="sendReQuestionMessage"
            class="chat-operate-textarea"
          />

          <div class="operate text-right">
            <el-button link @click="cancelReQuestion">
              <el-icon class="color-secondary"><Close /> </el-icon>
            </el-button>

            <el-divider direction="vertical" />
            <el-button
              text
              class="sent-button"
              :disabled="!editText.trim() || editText.trim() === chatRecord.problem_text.trim()"
              @click="sendReQuestionMessage"
            >
              <img
                v-show="!editText.trim() || editText.trim() === chatRecord.problem_text.trim()"
                src="@/assets/icon_send.svg"
                alt=""
              />
              <SendIcon
                v-show="editText.trim() && editText.trim() !== chatRecord.problem_text.trim()"
              />
            </el-button>
          </div>
        </div>
      </div>
      <!-- <el-input v-else v-model="editText">
        <template #append>
          <div class="flex" style="gap: 8px">
            <el-button-group class="flex ml-8 mr-8">
              <el-button class="flex mr-8" text @click="cancelReQuestion"
                ><el-icon><Close /></el-icon
              ></el-button>
              <el-button
                :disabled="!editText.trim() || editText.trim() === chatRecord.problem_text.trim()"
                text
                @click="sendReQuestionMessage(chatRecord)"
              >
                <el-icon><Comment /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </template>
      </el-input> -->
      <div class="avatar ml-8" v-if="showAvatar">
        <el-image
          v-if="application.user_avatar"
          :src="application.user_avatar"
          alt=""
          fit="cover"
          style="width: 28px; height: 28px; display: block"
        />
        <el-avatar v-else :size="28">
          <img src="@/assets/user-icon.svg" style="width: 50%" alt="" />
        </el-avatar>
      </div>
    </div>
    <div class="question-edit-button text-right mt-4">
      <div v-if="!isReQuestion && showIcon">
        <el-tooltip
          effect="dark"
          :content="$t('common.edit')"
          placement="top"
          v-if="props.isLast && props.type !== 'log'"
        >
          <el-button text @click.stop="handleEdit(chatRecord)">
            <AppIcon class="color-secondary" iconName="app-edit"></AppIcon>
          </el-button>
        </el-tooltip>
        <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
          <el-button text @click.stop="copyClick(chatRecord?.problem_text)">
            <AppIcon class="color-secondary" iconName="app-copy"></AppIcon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { type chatType } from '@/api/type/application'
import { getImgUrl, downloadByURL } from '@/utils/common'
import { useRoute, useRouter } from 'vue-router'
import { onMounted, computed, ref, nextTick } from 'vue'
import {getAttrsArray} from '@/utils/array'
import { copyClick } from '@/utils/clipboard'
const route = useRoute()
const {
  query: { mode },
} = route as any
const props = defineProps<{
  application: any
  chatRecord: chatType
  chatManagement: any
  sendMessage: (question: string, other_params_data?: any, chat?: chatType) => Promise<boolean>
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
  isLast: boolean
}>()

const showIcon = ref<boolean>(false)
const isReQuestion = ref<boolean>(false)
const editText = ref<string>('')
const direction = ref<'horizontal' | 'vertical'>('horizontal')

const showAvatar = computed(() => {
  return props.application.show_user_avatar == undefined ? true : props.application.show_user_avatar
})

const document_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.document_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node',
  )
  return startNode?.document_list || []
})
const image_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.image_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node',
  )
  return startNode?.image_list || []
})
const video_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.video_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node',
  )
  return startNode?.video_list || []
})
const audio_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.audio_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node',
  )
  return startNode?.audio_list || []
})
const other_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.other_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node',
  )
  return startNode?.other_list || []
})
const getClassName = computed(() => {
  return document_list.value.length >= 2 || other_list.value.length >= 2
    ? 'media_2'
    : document_list.value.length
      ? `media_${document_list.value.length}`
      : other_list.value.length
        ? `media_${other_list.value.length}`
        : `media_0`
})

function downloadFile(item: any) {
  downloadByURL(item.url, item.name)
}

function handleEdit(chatRecord: any) {
  isReQuestion.value = true
  editText.value = chatRecord.problem_text
}

const cancelReQuestion = () => {
  isReQuestion.value = false
}

const emit = defineEmits(['reQuestion'])
const quickInputRef = ref()
function sendReQuestionMessage(event?: any) {
  const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent,
  )
  // 如果是移动端，且按下回车键，不直接发送
  if ((isMobile || mode === 'mobile') && event?.key === 'Enter') {
    // 阻止默认事件
    return
  }
  if (!event?.ctrlKey && !event?.shiftKey && !event?.altKey && !event?.metaKey) {
    // 如果没有按下组合键，则会阻止默认事件
    event?.preventDefault()
    if (editText.value.trim() && editText.value.trim() !== props.chatRecord.problem_text.trim()) {
      const container = props.chatRecord?.upload_meta
        ? props.chatRecord.upload_meta
        : props.chatRecord.execution_details?.find((detail) => detail.type === 'start-node')

      props.chatRecord.problem_text = editText.value
      reset_answer_text_list(props.chatRecord.answer_text_list)
      props.chatRecord.write_ed = false

      isReQuestion.value = false
      props.sendMessage(
        editText.value,
        {
          re_chat: true,
          image_list: container?.image_list || [],
          document_list: container?.document_list || [],
          audio_list: container?.audio_list || [],
          video_list: container?.video_list || [],
          other_list: container?.other_list || [],
          chat_record_id: props.chatRecord.record_id
            ? props.chatRecord.record_id
            : props.chatRecord.id,
        },
        props.chatRecord,
      )
    }
  } else {
    // 如果同时按下ctrl/shift/cmd/opt +enter，则会换行
    insertNewlineAtCursor(event)
  }
}

const insertNewlineAtCursor = (event?: any) => {
  const textarea = quickInputRef.value.$el.querySelector(
    '.el-textarea__inner',
  ) as HTMLTextAreaElement
  const startPos = textarea.selectionStart
  const endPos = textarea.selectionEnd
  // 阻止默认行为（避免额外的换行符）
  event.preventDefault()
  // 在光标处插入换行符
  editText.value =
    editText.value.trim().slice(0, startPos) + '\n' + editText.value.trim().slice(endPos)
  nextTick(() => {
    textarea.setSelectionRange(startPos + 1, startPos + 1) // 光标定位到换行后位置
  })
}

const reset_answer_text_list = (answer_text_list: any) => {
  answer_text_list.splice(0, answer_text_list.length)
  answer_text_list.push([])
}

onMounted(() => {})
</script>
<style lang="scss" scoped>
.question-content {
  display: flex;
  justify-content: flex-end;
  padding-left: var(--padding-left);
  width: 100%;
  box-sizing: border-box;

  .content {
    background: #d6e2ff;
    padding-left: 16px;
    padding-right: 16px;
  }

  .download-file {
    height: 43px;

    &:hover {
      color: var(--el-color-primary);
      border: 1px solid var(--el-color-primary);

      .download-button {
        display: block;
        text-align: center;
        line-height: 26px;
      }

      .show {
        display: none;
      }
    }

    .download-button {
      display: none;
    }
  }

  .media-file-width {
    :deep(.el-space__item) {
      width: 49% !important;
    }
  }

  .media_2 {
    flex: 1;
  }

  .media_0 {
    flex: inherit;
  }

  .media_1 {
    width: 50%;
  }
}

.question-edit-button {
  height: 28px;
}

@media only screen and (max-width: 768px) {
  .question-content {
    .media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }

    .media_1 {
      width: 100%;
    }
  }
}

.debug-ai-chat {
  .question-content {
    .media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }

    .media_1 {
      width: 100%;
    }
  }
}

.question-content {
  &__operate {
    position: relative;
    width: 100%;
    box-sizing: border-box;
    z-index: 10;

    :deep(.operate-textarea) {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
      background-color: #ffffff;
      border-radius: 8px;
      border: 1px solid #ffffff;
      box-sizing: border-box;

      &:has(.el-textarea__inner:focus) {
        border: 1px solid var(--el-color-primary);
      }

      .el-textarea__inner {
        border-radius: 8px !important;
        box-shadow: none;
        resize: none;
        padding: 13px 16px;
        box-sizing: border-box;
        min-height: 47px !important;
        height: 0;
      }

      .operate {
        padding: 6px 10px;

        .el-icon {
          font-size: 20px;
        }

        .sent-button {
          max-height: none;

          .el-icon {
            font-size: 24px;
          }
        }

        .el-loading-spinner {
          margin-top: -15px;

          .circular {
            width: 31px;
            height: 31px;
          }
        }
      }
    }

    .file-image {
      position: relative;
      overflow: inherit;

      .delete-icon {
        position: absolute;
        right: -5px;
        top: -5px;
        z-index: 1;
      }
    }

    .upload-tooltip-width {
      width: 300px;
    }
  }
}
</style>
