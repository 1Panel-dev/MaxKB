<template>
  <div>
    <div class="flex-between mt-8">
      <div>
        <el-text type="info">
          <span class="ml-4">{{ datetimeFormat(data.create_time) }}</span>
        </el-text>
      </div>
      <div>
        <!-- 语音播放 -->
        <span v-if="tts">
          <el-tooltip
            effect="dark"
            :content="$t('chat.operation.play')"
            placement="top"
            v-if="!audioPlayerStatus"
          >
            <el-button text @click="playAnswerText(data?.answer_text)">
              <AppIcon iconName="app-video-play"></AppIcon>
            </el-button>
          </el-tooltip>
          <el-tooltip v-else effect="dark" :content="$t('chat.operation.pause')" placement="top">
            <el-button type="primary" text @click="pausePlayAnswerText()">
              <AppIcon iconName="app-video-pause"></AppIcon>
            </el-button>
          </el-tooltip>
          <el-divider direction="vertical" />
        </span>
        <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
          <el-button text @click="copyClick(data?.answer_text)">
            <AppIcon iconName="app-copy"></AppIcon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <template v-if="permissionPrecise.chat_log_add_knowledge(id)">
          <el-tooltip
            v-if="buttonData.improve_paragraph_id_list.length === 0"
            effect="dark"
            :content="$t('views.chatLog.editContent')"
            placement="top"
          >
            <el-button text @click="editContent(data)">
              <AppIcon iconName="app-edit"></AppIcon>
            </el-button>
          </el-tooltip>

          <el-tooltip v-else effect="dark" :content="$t('views.chatLog.editMark')" placement="top">
            <el-button text @click="editMark(data)">
              <AppIcon iconName="app-document-active" class="primary"></AppIcon>
            </el-button>
          </el-tooltip>
        </template>

        <el-divider direction="vertical" v-if="buttonData?.vote_status !== '-1'" />
        <el-button text disabled v-if="buttonData?.vote_status === '0'">
          <AppIcon iconName="app-like-color"></AppIcon>
        </el-button>

        <el-button text disabled v-if="buttonData?.vote_status === '1'">
          <AppIcon iconName="app-oppose-color"></AppIcon>
        </el-button>
        <EditContentDialog ref="EditContentDialogRef" @refresh="refreshContent" />
        <EditMarkDialog ref="EditMarkDialogRef" @refresh="refreshMark" />
        <!-- 先渲染，不然不能播放   -->
        <audio
          ref="audioPlayer"
          v-for="item in audioList"
          :key="item"
          controls
          hidden="hidden"
        ></audio>
      </div>
    </div>

    <el-card
      class="mt-16 layout-bg"
      shadow="always"
      v-if="buttonData?.vote_status !== '-1' && data.vote_reason"
    >
      <VoteReasonContent
        v-if="buttonData?.id"
        :vote-type="buttonData?.vote_status"
        :chat-id="buttonData?.chat_id"
        :record-id="buttonData?.id"
        readonly
        :default-reason="data.vote_reason"
        :default-other-content="data.vote_other_content"
      >
      </VoteReasonContent>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { copyClick } from '@/utils/clipboard'
import EditContentDialog from '@/views/chat-log/component/EditContentDialog.vue'
import EditMarkDialog from '@/views/chat-log/component/EditMarkDialog.vue'
import { datetimeFormat } from '@/utils/time'
import applicationApi from '@/api/application/application'
import { useRoute } from 'vue-router'
import permissionMap from '@/permission'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'
import VoteReasonContent from '@/components/ai-chat/component/operation-button/VoteReasonContent.vue'
const route = useRoute()
const {
  params: { id },
} = route as any

const props = defineProps({
  data: {
    type: Object,
    default: () => {},
  },
  applicationId: {
    type: String,
    default: '',
  },
  tts: Boolean,
  tts_type: String,
})

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['application'][apiType.value]
})

const emit = defineEmits(['update:data'])

const audioPlayer = ref<HTMLAudioElement[] | null>(null)

const EditContentDialogRef = ref()
const EditMarkDialogRef = ref()

const buttonData = ref(props.data)
const loading = ref(false)
const utterance = ref<SpeechSynthesisUtterance | null>(null)
const audioList = ref<string[]>([])
const currentAudioIndex = ref(0)

function editContent(data: any) {
  EditContentDialogRef.value.open(data)
}

function editMark(data: any) {
  EditMarkDialogRef.value.open(data)
}

const audioPlayerStatus = ref(false)

function markdownToPlainText(md: string) {
  return (
    md
      // 移除图片 ![alt](url)
      .replace(/!\[.*?\]\(.*?\)/g, '')
      // 移除链接 [text](url)
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      // 移除 Markdown 标题符号 (#, ##, ###)
      .replace(/^#{1,6}\s+/gm, '')
      // 移除加粗 **text** 或 __text__
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/__(.*?)__/g, '$1')
      // 移除斜体 *text* 或 _text_
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/_(.*?)_/g, '$1')
      // 移除行内代码 `code`
      .replace(/`(.*?)`/g, '$1')
      // 移除代码块 ```code```
      .replace(/```[\s\S]*?```/g, '')
      // 移除多余的换行符
      .replace(/\n{2,}/g, '\n')
      .trim()
  )
}

function removeFormRander(text: string) {
  return text.replace(/<form_rander>[\s\S]*?<\/form_rander>/g, '').trim()
}

const playAnswerText = (text: string) => {
  if (!text) {
    text = t('chat.tip.answerMessage')
  }
  // 移除表单渲染器
  text = removeFormRander(text)
  // text 处理成纯文本
  text = markdownToPlainText(text)
  // console.log(text)
  audioPlayerStatus.value = true
  // 分割成多份
  audioList.value = text.split(/(<audio[^>]*><\/audio>)/)
  playAnswerTextPart()
}

const playAnswerTextPart = () => {
  // console.log(audioList.value, currentAudioIndex.value)
  if (currentAudioIndex.value === audioList.value.length) {
    audioPlayerStatus.value = false
    currentAudioIndex.value = 0
    return
  }
  if (audioList.value[currentAudioIndex.value].includes('<audio')) {
    if (audioPlayer.value) {
      audioPlayer.value[currentAudioIndex.value].src =
        audioList.value[currentAudioIndex.value].match(/src="([^"]*)"/)?.[1] || ''
      audioPlayer.value[currentAudioIndex.value].play() // 自动播放音频
      audioPlayer.value[currentAudioIndex.value].onended = () => {
        currentAudioIndex.value += 1
        playAnswerTextPart()
      }
    }
  } else if (props.tts_type === 'BROWSER') {
    if (audioList.value[currentAudioIndex.value] !== utterance.value?.text) {
      window.speechSynthesis.cancel()
    }
    if (
      window.speechSynthesis.paused &&
      audioList.value[currentAudioIndex.value] === utterance.value?.text
    ) {
      window.speechSynthesis.resume()
      return
    }
    // 创建一个新的 SpeechSynthesisUtterance 实例
    utterance.value = new SpeechSynthesisUtterance(audioList.value[currentAudioIndex.value])
    utterance.value.onend = () => {
      utterance.value = null
      currentAudioIndex.value += 1
      playAnswerTextPart()
    }
    utterance.value.onerror = () => {
      audioPlayerStatus.value = false
      utterance.value = null
    }
    // 调用浏览器的朗读功能
    window.speechSynthesis.speak(utterance.value)
  } else if (props.tts_type === 'TTS') {
    // 恢复上次暂停的播放
    if (audioPlayer.value && audioPlayer.value[currentAudioIndex.value]?.src) {
      audioPlayer.value[currentAudioIndex.value].play()
      return
    }
    applicationApi
      .postTextToSpeech(
        (props.applicationId as string) || (id as string),
        { text: audioList.value[currentAudioIndex.value] },
        loading,
      )
      .then(async (res: any) => {
        if (res.type === 'application/json') {
          const text = await res.text()
          MsgError(text)
          return
        }
        // 假设我们有一个 MP3 文件的字节数组
        // 创建 Blob 对象
        const blob = new Blob([res], { type: 'audio/mp3' })

        // 创建对象 URL
        const url = URL.createObjectURL(blob)

        // 测试blob是否能正常播放
        // const link = document.createElement('a')
        // link.href = window.URL.createObjectURL(blob)
        // link.download = "abc.mp3"
        // link.click()

        // 检查 audioPlayer 是否已经引用了 DOM 元素
        if (audioPlayer.value) {
          audioPlayer.value[currentAudioIndex.value].src = url
          audioPlayer.value[currentAudioIndex.value].play() // 自动播放音频
          audioPlayer.value[currentAudioIndex.value].onended = () => {
            currentAudioIndex.value += 1
            playAnswerTextPart()
          }
        } else {
          console.error('audioPlayer.value is not an instance of HTMLAudioElement')
        }
      })
      .catch((err) => {
        console.log('err: ', err)
      })
  }
}

const pausePlayAnswerText = () => {
  audioPlayerStatus.value = false
  if (props.tts_type === 'TTS') {
    if (audioPlayer.value) {
      audioPlayer.value?.forEach((item) => {
        item.pause()
      })
    }
  }
  if (props.tts_type === 'BROWSER') {
    window.speechSynthesis.pause()
  }
}

function refreshMark() {
  buttonData.value.improve_paragraph_id_list = []
  emit('update:data', buttonData.value)
}
function refreshContent(data: any) {
  buttonData.value = data
  emit('update:data', buttonData.value)
}
</script>
<style lang="scss" scoped></style>
