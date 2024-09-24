<template>
  <div>
    <el-text type="info">
      <span class="ml-4">{{ datetimeFormat(data.create_time) }}</span>
    </el-text>
  </div>
  <div>
    <!-- 语音播放 -->
    <span v-if="tts">
      <el-tooltip effect="dark" content="点击播放" placement="top" v-if="!audioPlayerStatus">
        <el-button text :disabled="!data?.write_ed" @click="playAnswerText(data?.answer_text)">
          <AppIcon iconName="app-video-play"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-tooltip v-else effect="dark" content="停止" placement="top">
        <el-button type="primary" text :disabled="!data?.write_ed" @click="pausePlayAnswerText()">
          <AppIcon iconName="app-video-pause"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
    </span>
    <span v-if="applicationId">
      <el-tooltip effect="dark" content="换个答案" placement="top">
        <el-button :disabled="chat_loading" text @click="regeneration">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
      <el-tooltip effect="dark" content="复制" placement="top">
        <el-button text @click="copyClick(data?.answer_text)">
          <AppIcon iconName="app-copy"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
      <el-tooltip
        effect="dark"
        content="赞同"
        placement="top"
        v-if="buttonData?.vote_status === '-1'"
      >
        <el-button text @click="voteHandle('0')" :disabled="loading">
          <AppIcon iconName="app-like"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-tooltip
        effect="dark"
        content="取消赞同"
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
        content="反对"
        placement="top"
        v-if="buttonData?.vote_status === '-1'"
      >
        <el-button text @click="voteHandle('1')" :disabled="loading">
          <AppIcon iconName="app-oppose"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-tooltip
        effect="dark"
        content="取消反对"
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
  <audio ref="audioPlayer" controls hidden="hidden"></audio>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import applicationApi from '@/api/application'
import { datetimeFormat } from '@/utils/time'

const route = useRoute()
const {
  params: { id }
} = route as any

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  applicationId: {
    type: String,
    default: ''
  },
  chatId: {
    type: String,
    default: ''
  },
  chat_loading: {
    type: Boolean
  },
  log: Boolean,
  tts: Boolean,
  tts_type: String
})

const emit = defineEmits(['update:data', 'regeneration'])

const audioPlayer = ref<HTMLAudioElement | null>(null)
const audioPlayerStatus = ref(false)
const buttonData = ref(props.data)
const loading = ref(false)
const utterance = ref<SpeechSynthesisUtterance | null>(null)

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

const playAnswerText = (text: string) => {
  if (!text) {
    text = '抱歉，没有查找到相关内容，请重新描述您的问题或提供更多信息。'
  }
  // text 处理成纯文本
  text = markdownToPlainText(text)
  audioPlayerStatus.value = true
  if (props.tts_type === 'BROWSER') {
    if (text !== utterance.value?.text) {
      window.speechSynthesis.cancel()
    }
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume()
      return
    }
    // 创建一个新的 SpeechSynthesisUtterance 实例
    utterance.value = new SpeechSynthesisUtterance(text)
    utterance.value.onend = () => {
      audioPlayerStatus.value = false
      utterance.value = null
    }
    utterance.value.onerror = () => {
      audioPlayerStatus.value = false
      utterance.value = null
    }
    // 调用浏览器的朗读功能
    window.speechSynthesis.speak(utterance.value)
  }
  if (props.tts_type === 'TTS') {
    // 恢复上次暂停的播放
    if (audioPlayer.value?.src) {
      audioPlayer.value?.play()
      return
    }
    applicationApi
      .postTextToSpeech((props.applicationId as string) || (id as string), { text: text }, loading)
      .then((res: any) => {
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
        if (audioPlayer.value instanceof HTMLAudioElement) {
          audioPlayer.value.src = url
          audioPlayer.value.play() // 自动播放音频
          audioPlayer.value.onended = () => {
            audioPlayerStatus.value = false
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
    audioPlayer.value?.pause()
  }
  if (props.tts_type === 'BROWSER') {
    window.speechSynthesis.pause()
  }
}
</script>
<style lang="scss" scoped></style>
