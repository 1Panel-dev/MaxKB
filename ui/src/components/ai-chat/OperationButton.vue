<template>
  <div>
    <el-text type="info">
      <span class="ml-4">{{ datetimeFormat(data.create_time) }}</span>
    </el-text>
  </div>
  <div>
    <!-- 语音播放 -->
    <span v-if="tts">
      <el-tooltip effect="dark" content="语音播放" placement="top">
        <el-button text :disabled="!data?.write_ed" @click="playAnswerText(data?.answer_text)">
          <AppIcon iconName="VideoPlay"></AppIcon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
    </span>
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
  </div>
  <!-- 先渲染，不然不能播放   -->
  <audio ref="audioPlayer" controls hidden="hidden"></audio>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { copyClick } from '@/utils/clipboard'
import applicationApi from '@/api/application'
import { datetimeFormat } from '@/utils/time'
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
  tts: Boolean
})

const emit = defineEmits(['update:data', 'regeneration'])

const audioPlayer = ref<HTMLAudioElement | null>(null)
const buttonData = ref(props.data)
const loading = ref(false)

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

const playAnswerText = (text: string) => {
  if (props.data.tts_type === 'BROWSER') {
    // 创建一个新的 SpeechSynthesisUtterance 实例
    const utterance = new SpeechSynthesisUtterance(text)
    // 调用浏览器的朗读功能
    window.speechSynthesis.speak(utterance)
  }
  if (props.data.tts_type === 'TTS') {
    applicationApi
      .postTextToSpeech(props.data.id as string, { text: text }, loading)
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
        } else {
          console.error('audioPlayer.value is not an instance of HTMLAudioElement')
        }
      })
      .catch((err) => {
        console.log('err: ', err)
      })
  }
}
</script>
<style lang="scss" scoped></style>
