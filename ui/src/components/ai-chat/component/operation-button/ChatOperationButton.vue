<template>
  <div>
    <el-text type="info">
      <span class="ml-4">{{ datetimeFormat(data.create_time) }}</span>
    </el-text>
  </div>
  <div>
    <!-- 语音播放 -->
    <span v-if="tts">
      <el-tooltip effect="dark" :content="$t('chat.operation.play')" placement="top" v-if="!audioPlayerStatus">
        <el-button text :disabled="!data?.write_ed" @click="playAnswerText(data?.answer_text)">
          <AppIcon iconName="app-video-play"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-tooltip v-else effect="dark" :content="$t('chat.operation.pause')" placement="top">
        <el-button type="primary" text :disabled="!data?.write_ed" @click="pausePlayAnswerText()">
          <AppIcon iconName="app-video-pause"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
    </span>
    <span v-if="type == 'ai-chat' || type == 'log'">
      <el-tooltip effect="dark" :content="$t('chat.operation.regeneration')" placement="top">
        <el-button :disabled="chat_loading" text @click="regeneration">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
      <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
        <el-button text @click="copyClick(data?.answer_text.trim())">
          <AppIcon iconName="app-copy"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
      <el-tooltip
        effect="dark"
        :content="$t('chat.operation.like')"
        placement="top"
        v-if="buttonData?.vote_status === '-1'"
      >
        <el-button text @click="voteHandle('0')" :disabled="loading">
          <AppIcon iconName="app-like"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-tooltip
        effect="dark"
        :content="$t('chat.operation.cancelLike')"
        placement="top"
        v-if="buttonData?.vote_status === '0'"
      >
        <el-button text @click="voteHandle('-1')" :disabled="loading">
          <AppIcon iconName="app-like-color"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" v-if="buttonData?.vote_status === '-1'" />
      <el-tooltip
        effect="dark"
        :content="$t('chat.operation.oppose')"
        placement="top"
        v-if="buttonData?.vote_status === '-1'"
      >
        <el-button text @click="voteHandle('1')" :disabled="loading">
          <AppIcon iconName="app-oppose"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-tooltip
        effect="dark"
        :content="$t('chat.operation.cancelOppose')"
        placement="top"
        v-if="buttonData?.vote_status === '1'"
      >
        <el-button text @click="voteHandle('-1')" :disabled="loading">
          <AppIcon iconName="app-oppose-color"></AppIcon>
        </el-button>
      </el-tooltip>
    </span>
  </div>
  <!-- 先渲染，不然不能播放   -->
  <audio ref="audioPlayer" v-for="item in audioList" :key="item" controls hidden="hidden"></audio>
</template>
<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import applicationApi from '@/api/application'
import { datetimeFormat } from '@/utils/time'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'
const route = useRoute()
const {
  params: { id }
} = route as any

const props = withDefaults(
  defineProps<{
    data: any
    type: 'log' | 'ai-chat' | 'debug-ai-chat'
    chatId: string
    chat_loading: boolean
    applicationId: string
    tts: boolean
    tts_type: string
    tts_autoplay: boolean
  }>(),
  {
    data: () => ({}),
    type: 'ai-chat'
  }
)

const emit = defineEmits(['update:data', 'regeneration'])

const audioPlayer = ref<HTMLAudioElement[] | null>([])
const audioPlayerStatus = ref(false)
const buttonData = ref(props.data)
const loading = ref(false)
const utterance = ref<SpeechSynthesisUtterance | null>(null)
const audioList = ref<string[]>([])
const currentAudioIndex = ref(0)

function regeneration() {
  emit('regeneration')
}

function voteHandle(val: string) {
  applicationApi
    .putChatVote(props.applicationId, props.chatId, props.data.record_id, val, loading)
    .then(() => {
      buttonData.value['vote_status'] = val
      emit('update:data', buttonData.value)
    })
}

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
  return text
    .replace(/<form_rander>[\s\S]*?<\/form_rander>/g, '')
    .trim()
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
  audioList.value = text.split(/(<audio[^>]*><\/audio>)/).filter((item) => item.trim().length > 0)
  nextTick(()=>{
    // console.log(audioList.value, audioPlayer.value)
    playAnswerTextPart()
  })
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
      audioPlayer.value[currentAudioIndex.value].src = audioList.value[currentAudioIndex.value].match(/src="([^"]*)"/)?.[1] || ''
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
    if (window.speechSynthesis.paused && audioList.value[currentAudioIndex.value] === utterance.value?.text) {
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
      .postTextToSpeech((props.applicationId as string) || (id as string), { text: audioList.value[currentAudioIndex.value] }, loading)
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

onMounted(() => {
  // 第一次回答后自动播放， 打开历史记录不自动播放
  if (props.tts && props.tts_autoplay && buttonData.value.write_ed && !buttonData.value.update_time) {
    playAnswerText(buttonData.value.answer_text)
  }
})
</script>
<style lang="scss" scoped></style>
