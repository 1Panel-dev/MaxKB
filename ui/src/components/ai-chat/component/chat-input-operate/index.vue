<template>
  <div class="ai-chat__operate p-16">
    <slot name="operateBefore" />
    <div class="operate-textarea">
      <el-scrollbar max-height="136">
        <div
          class="p-8-12"
          v-loading="localLoading"
          v-if="
            uploadDocumentList.length ||
            uploadImageList.length ||
            uploadAudioList.length ||
            uploadVideoList.length
          "
        >
          <el-row :gutter="10">
            <el-col
              v-for="(item, index) in uploadDocumentList"
              :key="index"
              :xs="24"
              :sm="props.type === 'debug-ai-chat' ? 24 : 12"
              :md="props.type === 'debug-ai-chat' ? 24 : 12"
              :lg="props.type === 'debug-ai-chat' ? 24 : 12"
              :xl="props.type === 'debug-ai-chat' ? 24 : 12"
              class="mb-8"
            >
              <el-card
                shadow="never"
                style="--el-card-padding: 8px; max-width: 100%"
                class="file cursor"
              >
                <div
                  class="flex align-center"
                  @mouseenter.stop="mouseenter(item)"
                  @mouseleave.stop="mouseleave()"
                >
                  <div
                    @click="deleteFile(index, 'document')"
                    class="delete-icon color-secondary"
                    v-if="showDelete === item.url"
                  >
                    <el-icon>
                      <CircleCloseFilled />
                    </el-icon>
                  </div>
                  <img :src="getImgUrl(item && item?.name)" alt="" width="24" />
                  <div class="ml-4 ellipsis-1" :title="item && item?.name">
                    {{ item && item?.name }}
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col
              :xs="24"
              :sm="props.type === 'debug-ai-chat' ? 24 : 12"
              :md="props.type === 'debug-ai-chat' ? 24 : 12"
              :lg="props.type === 'debug-ai-chat' ? 24 : 12"
              :xl="props.type === 'debug-ai-chat' ? 24 : 12"
              class="mb-8"
              v-for="(item, index) in uploadAudioList"
              :key="index"
            >
              <el-card shadow="never" style="--el-card-padding: 8px" class="file cursor">
                <div
                  class="flex align-center"
                  @mouseenter.stop="mouseenter(item)"
                  @mouseleave.stop="mouseleave()"
                >
                  <div
                    @click="deleteFile(index, 'audio')"
                    class="delete-icon color-secondary"
                    v-if="showDelete === item.url"
                  >
                    <el-icon>
                      <CircleCloseFilled />
                    </el-icon>
                  </div>
                  <img :src="getImgUrl(item && item?.name)" alt="" width="24" />
                  <div class="ml-4 ellipsis-1" :title="item && item?.name">
                    {{ item && item?.name }}
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          <el-space wrap>
            <template v-for="(item, index) in uploadImageList" :key="index">
              <div
                class="file cursor border border-r-4"
                v-if="item.url"
                @mouseenter.stop="mouseenter(item)"
                @mouseleave.stop="mouseleave()"
              >
                <div
                  @click="deleteFile(index, 'image')"
                  class="delete-icon color-secondary"
                  v-if="showDelete === item.url"
                >
                  <el-icon>
                    <CircleCloseFilled />
                  </el-icon>
                </div>
                <el-image
                  :src="item.url"
                  alt=""
                  fit="cover"
                  style="width: 40px; height: 40px; display: block"
                  class="border-r-4"
                />
              </div>
            </template>
          </el-space>
        </div>
      </el-scrollbar>
      <div class="flex">
        <TouchChat
          v-if="isMicrophone"
          @TouchStart="startRecording"
          @TouchEnd="TouchEnd"
          :time="recorderTime"
          :start="!mediaRecorderStatus"
        />
        <el-input
          v-else
          ref="quickInputRef"
          v-model="inputValue"
          :placeholder="
            startRecorderTime
              ? `${$t('chat.inputPlaceholder.speaking')}...`
              : recorderLoading
                ? `${$t('chat.inputPlaceholder.recorderLoading')}...`
                : $t('chat.inputPlaceholder.default')
          "
          :autosize="{ minRows: 1, maxRows: isMobile ? 4 : 10 }"
          type="textarea"
          :maxlength="100000"
          @keydown.enter="sendChatHandle($event)"
        />

        <div class="operate flex align-center">
          <template v-if="props.applicationDetails.stt_model_enable">
            <span v-if="mode === 'mobile'">
              <el-button text @click="isMicrophone = !isMicrophone">
                <AppIcon v-if="isMicrophone" iconName="app-keyboard"></AppIcon>
                <el-icon v-else>
                  <Microphone />
                </el-icon>
              </el-button>
            </span>
            <span class="flex align-center" v-else>
              <el-button text @click="startRecording" v-if="mediaRecorderStatus">
                <el-icon>
                  <Microphone />
                </el-icon>
              </el-button>

              <div v-else class="operate flex align-center">
                <el-text type="info"
                  >00:{{ recorderTime < 10 ? `0${recorderTime}` : recorderTime }}</el-text
                >
                <el-button text type="primary" @click="stopRecording" :loading="recorderLoading">
                  <AppIcon iconName="app-video-stop"></AppIcon>
                </el-button>
              </div>
            </span>
          </template>

          <template v-if="!startRecorderTime && !recorderLoading">
            <span v-if="props.applicationDetails.file_upload_enable" class="flex align-center ml-4">
              <el-upload
                action="#"
                multiple
                :auto-upload="false"
                :show-file-list="false"
                :accept="getAcceptList()"
                :on-change="(file: any, fileList: any) => uploadFile(file, fileList)"
              >
                <el-tooltip
                  :disabled="mode === 'mobile'"
                  effect="dark"
                  placement="top"
                  popper-class="upload-tooltip-width"
                >
                  <template #content>
                    <div class="break-all pre-wrap">
                      {{ $t('chat.uploadFile.label') }}：{{ $t('chat.uploadFile.most')
                      }}{{ props.applicationDetails.file_upload_setting.maxFiles
                      }}{{ $t('chat.uploadFile.limit') }}
                      {{ props.applicationDetails.file_upload_setting.fileLimit }}MB<br />{{
                        $t('chat.uploadFile.fileType')
                      }}：{{ getAcceptList().replace(/\./g, '').replace(/,/g, '、').toUpperCase() }}
                    </div>
                  </template>
                  <el-button text :disabled="checkMaxFilesLimit()" class="mt-4">
                    <el-icon><Paperclip /></el-icon>
                  </el-button>
                </el-tooltip>
              </el-upload>
            </span>
            <el-divider
              direction="vertical"
              v-if="
                props.applicationDetails.file_upload_enable ||
                props.applicationDetails.stt_model_enable
              "
            />
            <el-button
              text
              class="sent-button"
              :disabled="isDisabledChat || loading"
              @click="sendChatHandle"
            >
              <img v-show="isDisabledChat || loading" src="@/assets/icon_send.svg" alt="" />
              <SendIcon v-show="!isDisabledChat && !loading" />
            </el-button>
          </template>
        </div>
      </div>
    </div>
    <div class="text-center" v-if="applicationDetails.disclaimer" style="margin-top: 8px">
      <el-text type="info" v-if="applicationDetails.disclaimer" style="font-size: 12px">
        <auto-tooltip :content="applicationDetails.disclaimer_value">
          {{ applicationDetails.disclaimer_value }}
        </auto-tooltip>
      </el-text>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import Recorder from 'recorder-core'
import TouchChat from './TouchChat.vue'
import applicationApi from '@/api/application'
import { MsgAlert } from '@/utils/message'
import { type chatType } from '@/api/type/application'
import { useRoute, useRouter } from 'vue-router'
import { getImgUrl } from '@/utils/utils'
import bus from '@/bus'
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine'
import { MsgWarning } from '@/utils/message'
import { t } from '@/locales'
const router = useRouter()
const route = useRoute()
const {
  query: { mode, question }
} = route as any
const quickInputRef = ref()
const props = withDefaults(
  defineProps<{
    applicationDetails: any
    type: 'log' | 'ai-chat' | 'debug-ai-chat'
    loading: boolean
    isMobile: boolean
    appId?: string
    chatId: string
    sendMessage: (question: string, other_params_data?: any, chat?: chatType) => void
    openChatId: () => Promise<string>
  }>(),
  {
    applicationDetails: () => ({}),
    available: true
  }
)
const emit = defineEmits(['update:chatId', 'update:loading'])
const chartOpenId = ref<string>()
const chatId_context = computed({
  get: () => {
    if (chartOpenId.value) {
      return chartOpenId.value
    }
    return props.chatId
  },
  set: (v) => {
    chartOpenId.value = v
    emit('update:chatId', v)
  }
})
const localLoading = computed({
  get: () => {
    return props.loading
  },
  set: (v) => {
    emit('update:loading', v)
  }
})

const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
const documentExtensions = ['pdf', 'docx', 'txt', 'xls', 'xlsx', 'md', 'html', 'csv']
const videoExtensions = ['mp4', 'avi', 'mov', 'mkv', 'flv']
const audioExtensions = ['mp3', 'wav', 'ogg', 'aac', 'm4a']

const getAcceptList = () => {
  const { image, document, audio, video } = props.applicationDetails.file_upload_setting
  let accepts: any = []
  if (image) {
    accepts = [...imageExtensions]
  }
  if (document) {
    accepts = [...accepts, ...documentExtensions]
  }
  if (audio) {
    accepts = [...accepts, ...audioExtensions]
  }
  if (video) {
    accepts = [...accepts, ...videoExtensions]
  }

  if (accepts.length === 0) {
    return `.${t('chat.uploadFile.tipMessage')}`
  }
  return accepts.map((ext: any) => '.' + ext).join(',')
}

const checkMaxFilesLimit = () => {
  return (
    props.applicationDetails.file_upload_setting.maxFiles <=
    uploadImageList.value.length +
      uploadDocumentList.value.length +
      uploadAudioList.value.length +
      uploadVideoList.value.length
  )
}

const uploadFile = async (file: any, fileList: any) => {
  const { maxFiles, fileLimit } = props.applicationDetails.file_upload_setting
  // 单次上传文件数量限制
  const file_limit_once =
    uploadImageList.value.length +
    uploadDocumentList.value.length +
    uploadAudioList.value.length +
    uploadVideoList.value.length
  if (file_limit_once >= maxFiles) {
    MsgWarning(t('chat.uploadFile.limitMessage1') + maxFiles + t('chat.uploadFile.limitMessage2'))
    fileList.splice(0, fileList.length)
    return
  }
  if (fileList.filter((f: any) => f.size > fileLimit * 1024 * 1024).length > 0) {
    // MB
    MsgWarning(t('chat.uploadFile.sizeLimit') + fileLimit + 'MB')
    fileList.splice(0, fileList.length)
    return
  }

  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  //
  const extension = file.name.split('.').pop().toLowerCase() // 获取文件后缀名并转为小写

  if (imageExtensions.includes(extension)) {
    uploadImageList.value.push(file)
  } else if (documentExtensions.includes(extension)) {
    uploadDocumentList.value.push(file)
  } else if (videoExtensions.includes(extension)) {
    uploadVideoList.value.push(file)
  } else if (audioExtensions.includes(extension)) {
    uploadAudioList.value.push(file)
  }

  if (!chatId_context.value) {
    const res = await props.openChatId()
    chatId_context.value = res
  }

  if (props.type === 'debug-ai-chat') {
    formData.append('debug', 'true')
  } else {
    formData.append('debug', 'false')
  }

  applicationApi
    .uploadFile(
      props.applicationDetails.id as string,
      chatId_context.value as string,
      formData,
      localLoading
    )
    .then((response) => {
      fileList.splice(0, fileList.length)
      uploadImageList.value.forEach((file: any) => {
        const f = response.data.filter((f: any) => f.name === file.name)
        if (f.length > 0) {
          file.url = f[0].url
          file.file_id = f[0].file_id
        }
      })
      uploadDocumentList.value.forEach((file: any) => {
        const f = response.data.filter((f: any) => f.name === file.name)
        if (f.length > 0) {
          file.url = f[0].url
          file.file_id = f[0].file_id
        }
      })
      uploadAudioList.value.forEach((file: any) => {
        const f = response.data.filter((f: any) => f.name === file.name)
        if (f.length > 0) {
          file.url = f[0].url
          file.file_id = f[0].file_id
        }
      })
      uploadVideoList.value.forEach((file: any) => {
        const f = response.data.filter((f: any) => f.name === file.name)
        if (f.length > 0) {
          file.url = f[0].url
          file.file_id = f[0].file_id
        }
      })
      if (!inputValue.value && uploadImageList.value.length > 0) {
        inputValue.value = t('chat.uploadFile.imageMessage')
      }
    })
}

const intervalId = ref<any | null>(null)
const recorderTime = ref(0)
const startRecorderTime = ref(false)
const recorderLoading = ref(false)
const inputValue = ref<string>('')
const uploadImageList = ref<Array<any>>([])
const uploadDocumentList = ref<Array<any>>([])
const uploadVideoList = ref<Array<any>>([])
const uploadAudioList = ref<Array<any>>([])
const mediaRecorderStatus = ref(true)
const showDelete = ref('')

// 定义响应式引用
const mediaRecorder = ref<any>(null)
const isDisabledChat = computed(
  () => !(inputValue.value.trim() && (props.appId || props.applicationDetails?.name))
)
// 移动端语音
const isMicrophone = ref(false)

const TouchEnd = (bool: Boolean) => {
  if (bool) {
    stopRecording()
  } else {
    stopTimer()
    mediaRecorder.value.close()
    mediaRecorder.value = null
  }
}

// 开始录音
const startRecording = async () => {
  try {
    // 取消录音控制台日志
    Recorder.CLog = function () {}
    mediaRecorder.value = new Recorder({
      type: 'mp3',
      bitRate: 128,
      sampleRate: 16000
    })

    mediaRecorder.value.open(
      () => {
        mediaRecorder.value.start()
        mediaRecorderStatus.value = false
        handleTimeChange()
      },
      (err: any) => {
        stopTimer()
        mediaRecorder.value.close()
        MsgAlert(
          t('common.tip'),
          `${t('chat.tip.recorderTip')}
    <img src="${new URL(`@/assets/tipIMG.jpg`, import.meta.url).href}" style="width: 100%;" />`,
          {
            confirmButtonText: t('chat.tip.confirm'),
            dangerouslyUseHTMLString: true,
            customClass: 'record-tip-confirm'
          }
        )
      }
    )
  } catch (error) {
    MsgAlert(
      t('common.tip'),
      `${t('chat.tip.recorderTip')}
    <img src="${new URL(`@/assets/tipIMG.jpg`, import.meta.url).href}" style="width: 100%;" />`,
      {
        confirmButtonText: t('chat.tip.confirm'),
        dangerouslyUseHTMLString: true,
        customClass: 'record-tip-confirm'
      }
    )
    mediaRecorder.value.close()
    stopTimer()
  }
}

// 停止录音
const stopRecording = () => {
  startRecorderTime.value = false
  recorderTime.value = 0
  if (mediaRecorder.value) {
    mediaRecorderStatus.value = true
    mediaRecorder.value.stop(
      (blob: Blob, duration: number) => {
        // 测试blob是否能正常播放
        //  const link = document.createElement('a')
        //  link.href = window.URL.createObjectURL(blob)
        //  link.download = 'abc.mp3'
        //  link.click()
        uploadRecording(blob) // 上传录音文件
      },
      (err: any) => {
        console.error(`${t('chat.tip.recorderError')}:`, err)
      }
    )
  }
}

// 上传录音文件
const uploadRecording = async (audioBlob: Blob) => {
  try {
    recorderLoading.value = true
    const formData = new FormData()
    formData.append('file', audioBlob, 'recording.mp3')
    applicationApi
      .postSpeechToText(props.applicationDetails.id as string, formData, localLoading)
      .then((response) => {
        recorderLoading.value = false
        mediaRecorder.value.close()
        inputValue.value = typeof response.data === 'string' ? response.data : ''
        // 自动发送
        if (props.applicationDetails.stt_autosend) {
          nextTick(() => {
            autoSendMessage()
          })
        } else {
          isMicrophone.value = false
        }
      })
      .catch((error) => {
        recorderLoading.value = false
        console.error(`${t('chat.uploadFile.errorMessage')}:`, error)
      })
  } catch (error) {
    recorderLoading.value = false
    console.error(`${t('chat.uploadFile.errorMessage')}:`, error)
  }
}

const handleTimeChange = () => {
  startRecorderTime.value = true
  recorderTime.value = 0
  intervalId.value = setInterval(() => {
    if (!startRecorderTime.value) {
      clearInterval(intervalId.value!)
      intervalId.value = null
      return
    }

    recorderTime.value++

    if (recorderTime.value === 60) {
      stopRecording()
      clearInterval(intervalId.value!)
      intervalId.value = null
      startRecorderTime.value = false
    }
  }, 1000)
}
// 停止计时的函数
const stopTimer = () => {
  if (intervalId.value !== null) {
    clearInterval(intervalId.value)
    intervalId.value = null
    startRecorderTime.value = false
    mediaRecorderStatus.value = true
  }
}

function autoSendMessage() {
  props.sendMessage(inputValue.value, {
    image_list: uploadImageList.value,
    document_list: uploadDocumentList.value,
    audio_list: uploadAudioList.value,
    video_list: uploadVideoList.value
  })
  inputValue.value = ''
  uploadImageList.value = []
  uploadDocumentList.value = []
  uploadAudioList.value = []
  uploadVideoList.value = []
  quickInputRef.value.textareaStyle.height = '45px'
}

function sendChatHandle(event?: any) {
  if (!event?.ctrlKey && !event?.shiftKey && !event?.altKey && !event?.metaKey) {
    // 如果没有按下组合键，则会阻止默认事件
    event?.preventDefault()
    if (!isDisabledChat.value && !props.loading && !event?.isComposing) {
      if (inputValue.value.trim()) {
        autoSendMessage()
      }
    }
  } else {
    // 如果同时按下ctrl/shift/cmd/opt +enter，则会换行
    insertNewlineAtCursor(event)
  }
}
const insertNewlineAtCursor = (event?: any) => {
  const textarea = document.querySelector('.el-textarea__inner') as HTMLTextAreaElement
  const startPos = textarea.selectionStart
  const endPos = textarea.selectionEnd
  // 阻止默认行为（避免额外的换行符）
  event.preventDefault()
  // 在光标处插入换行符
  inputValue.value = inputValue.value.slice(0, startPos) + '\n' + inputValue.value.slice(endPos)
  nextTick(() => {
    textarea.setSelectionRange(startPos + 1, startPos + 1) // 光标定位到换行后位置
  })
}

function deleteFile(index: number, val: string) {
  if (val === 'image') {
    uploadImageList.value.splice(index, 1)
  } else if (val === 'document') {
    uploadDocumentList.value.splice(index, 1)
  } else if (val === 'video') {
    uploadVideoList.value.splice(index, 1)
  } else if (val === 'audio') {
    uploadAudioList.value.splice(index, 1)
  }
}

function mouseenter(row: any) {
  showDelete.value = row.url
}

function mouseleave() {
  showDelete.value = ''
}

onMounted(() => {
  bus.on('chat-input', (message: string) => {
    inputValue.value = message
  })
  if (question) {
    inputValue.value = decodeURIComponent(question.trim())
    sendChatHandle()
    setTimeout(() => {
      // 获取当前路由信息
      const route = router.currentRoute.value
      // 复制query对象
      const query = { ...route.query }
      // 删除特定的参数
      delete query.question
      const newRoute =
        Object.entries(query)?.length > 0
          ? route.path +
            '?' +
            Object.entries(query)
              .map(([key, value]) => `${key}=${value}`)
              .join('&')
          : route.path

      history.pushState(null, '', '/ui' + newRoute)
    }, 100)
  }
  setTimeout(() => {
    if (quickInputRef.value && mode === 'embed') {
      quickInputRef.value.textarea.style.height = '0'
    }
  }, 1800)
})
</script>
<style lang="scss" scoped>
.ai-chat {
  &__operate {
    background: #f3f7f9;
    position: relative;
    width: 100%;
    box-sizing: border-box;
    z-index: 10;

    &:before {
      background: linear-gradient(0deg, #f3f7f9 0%, rgba(243, 247, 249, 0) 100%);
      content: '';
      position: absolute;
      width: 100%;
      top: -16px;
      left: 0;
      height: 16px;
    }

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
    .file {
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

@media only screen and (max-width: 768px) {
  .ai-chat {
    height: calc(100% - 100px);
    &__operate {
      position: fixed;
      bottom: 0;
      font-size: 1rem;
      .el-icon {
        font-size: 1.4rem !important;
      }
    }
  }
}
.chat-pc {
}
</style>
