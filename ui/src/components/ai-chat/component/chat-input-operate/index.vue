<template>
  <div></div>
  <div class="ai-chat__operate p-16-24">
    <slot name="operateBefore" />
    <div class="operate-textarea flex chat-width">
      <el-input
        ref="quickInputRef"
        v-model="inputValue"
        :placeholder="
          startRecorderTime
            ? '说话中...'
            : recorderLoading
              ? '转文字中...'
              : '请输入问题，Ctrl+Enter 换行，Enter发送'
        "
        :autosize="{ minRows: 1, maxRows: isMobile ? 4 : 10 }"
        type="textarea"
        :maxlength="100000"
        @keydown.enter="sendChatHandle($event)"
      />

      <div class="operate flex align-center">
        <span v-if="props.applicationDetails.file_upload_enable" class="flex align-center">
          <el-upload
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file: any, fileList: any) => uploadFile(file, fileList)"
          >
            <el-button text>
              <el-icon><Paperclip /></el-icon>
            </el-button>
          </el-upload>
          <el-divider direction="vertical" />
        </span>
        <span v-if="props.applicationDetails.stt_model_enable" class="flex align-center">
          <el-button text v-if="mediaRecorderStatus" @click="startRecording">
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
          <el-divider v-if="!startRecorderTime && !recorderLoading" direction="vertical" />
        </span>

        <el-button
          v-if="!startRecorderTime && !recorderLoading"
          text
          class="sent-button"
          :disabled="isDisabledChart || loading"
          @click="sendChatHandle"
        >
          <img v-show="isDisabledChart || loading" src="@/assets/icon_send.svg" alt="" />
          <SendIcon v-show="!isDisabledChart && !loading" />
        </el-button>
      </div>
    </div>
    <div
      class="chat-width text-center"
      v-if="applicationDetails.disclaimer"
      style="margin-top: 8px"
    >
      <el-text type="info" v-if="applicationDetails.disclaimer" style="font-size: 12px">
        <auto-tooltip :content="applicationDetails.disclaimer_value">
          {{ applicationDetails.disclaimer_value }}
        </auto-tooltip>
      </el-text>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Recorder from 'recorder-core'
import applicationApi from '@/api/application'
import { MsgAlert } from '@/utils/message'
import { type chatType } from '@/api/type/application'
import { useRoute } from 'vue-router'
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine'
import { MsgWarning } from '@/utils/message'
const route = useRoute()
const {
  query: { mode }
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
const uploadFile = async (file: any, fileList: any) => {
  const { maxFiles, fileLimit } = props.applicationDetails.file_upload_setting
  if (fileList.length > maxFiles) {
    MsgWarning('最多上传' + maxFiles + '个文件')
    return
  }
  if (fileList.filter((f: any) => f.size > fileLimit * 1024 * 1024).length > 0) {
    // MB
    MsgWarning('单个文件大小不能超过' + fileLimit + 'MB')
    fileList.splice(0, fileList.length)
    return
  }
  const formData = new FormData()
  for (const file of fileList) {
    formData.append('file', file.raw, file.name)
    uploadFileList.value.push(file)
  }

  if (!chatId_context.value) {
    const res = await applicationApi.getChatOpen(props.applicationDetails.id as string)
    chatId_context.value = res.data
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
      uploadFileList.value.forEach((file: any) => {
        const f = response.data.filter((f: any) => f.name === file.name)
        if (f.length > 0) {
          file.url = f[0].url
          file.file_id = f[0].file_id
        }
      })
      console.log(uploadFileList.value)
    })
}
const recorderTime = ref(0)
const startRecorderTime = ref(false)
const recorderLoading = ref(false)
const inputValue = ref<string>('')
const uploadFileList = ref<Array<any>>([])
const mediaRecorderStatus = ref(true)
// 定义响应式引用
const mediaRecorder = ref<any>(null)
const isDisabledChart = computed(
  () => !(inputValue.value.trim() && (props.appId || props.applicationDetails?.name))
)

// 开始录音
const startRecording = async () => {
  try {
    // 取消录音控制台日志
    Recorder.CLog = function () {}
    mediaRecorderStatus.value = false
    handleTimeChange()
    mediaRecorder.value = new Recorder({
      type: 'mp3',
      bitRate: 128,
      sampleRate: 16000
    })

    mediaRecorder.value.open(
      () => {
        mediaRecorder.value.start()
      },
      (err: any) => {
        MsgAlert(
          `提示`,
          `<p>该功能需要使用麦克风，浏览器禁止不安全页面录音，解决方案如下：<br/>
1、可开启 https 解决；<br/>
2、若无 https 配置则需要修改浏览器安全配置，Chrome 设置如下：<br/>
(1) 地址栏输入chrome://flags/#unsafely-treat-insecure-origin-as-secure；<br/>
(2) 将 http 站点配置在文本框中，例如: http://127.0.0.1:8080。</p>
    <img src="${new URL(`../../assets/tipIMG.jpg`, import.meta.url).href}" style="width: 100%;" />`,
          {
            confirmButtonText: '我知道了',
            dangerouslyUseHTMLString: true,
            customClass: 'record-tip-confirm'
          }
        )
      }
    )
  } catch (error) {
    MsgAlert(
      `提示`,
      `<p>该功能需要使用麦克风，浏览器禁止不安全页面录音，解决方案如下：<br/>
1、可开启 https 解决；<br/>
2、若无 https 配置则需要修改浏览器安全配置，Chrome 设置如下：<br/>
(1) 地址栏输入chrome://flags/#unsafely-treat-insecure-origin-as-secure；<br/>
(2) 将 http 站点配置在文本框中，例如: http://127.0.0.1:8080。</p>
    <img src="${new URL(`../../assets/tipIMG.jpg`, import.meta.url).href}" style="width: 100%;" />`,
      {
        confirmButtonText: '我知道了',
        dangerouslyUseHTMLString: true,
        customClass: 'record-tip-confirm'
      }
    )
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
        console.error('录音失败:', err)
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
        // chatMessage(null, res.data)
      })
  } catch (error) {
    recorderLoading.value = false
    console.error('上传失败:', error)
  }
}
const handleTimeChange = () => {
  startRecorderTime.value = true

  setTimeout(() => {
    if (recorderTime.value === 60) {
      recorderTime.value = 0
      stopRecording()
      startRecorderTime.value = false
    }
    if (!startRecorderTime.value) {
      return
    }
    recorderTime.value++
    handleTimeChange()
  }, 1000)
}
function sendChatHandle(event: any) {
  if (!event.ctrlKey) {
    // 如果没有按下组合键ctrl，则会阻止默认事件
    event.preventDefault()
    if (!isDisabledChart.value && !props.loading && !event.isComposing) {
      if (inputValue.value.trim()) {
        props.sendMessage(inputValue.value, { image_list: uploadFileList.value })
        inputValue.value = ''
        uploadFileList.value = []
        quickInputRef.value.textareaStyle.height = '45px'
      }
    }
  } else {
    // 如果同时按下ctrl+回车键，则会换行
    inputValue.value += '\n'
  }
}
onMounted(() => {
  setTimeout(() => {
    if (quickInputRef.value && mode === 'embed') {
      quickInputRef.value.textarea.style.height = '0'
    }
  }, 1800)
})
</script>
<style lang="scss" scope>
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

    .operate-textarea {
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
        padding: 12px 16px;
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
  }
}

.chat-width {
  max-width: 80%;
  margin: 0 auto;
}
@media only screen and (max-width: 1000px) {
  .chat-width {
    max-width: 100% !important;
    margin: 0 auto;
  }
}
</style>
