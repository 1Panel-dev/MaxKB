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
        <el-button v-if="!audioPlayerStatus" text @click="playAnswerText(data?.answer_text)">
          <AppIcon iconName="app-video-play"></AppIcon>
        </el-button>
        <el-button v-else text @click="pausePlayAnswerText()">
          <el-icon><VideoPause /></el-icon>
        </el-button>
      </el-tooltip>
      <el-divider direction="vertical" />
    </span>
    <el-tooltip effect="dark" content="复制" placement="top">
      <el-button text @click="copyClick(data?.answer_text)">
        <AppIcon iconName="app-copy"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" />
    <el-tooltip
      v-if="data.improve_paragraph_id_list.length === 0"
      effect="dark"
      content="修改内容"
      placement="top"
    >
      <el-button text @click="editContent(data)">
        <el-icon><EditPen /></el-icon>
      </el-button>
    </el-tooltip>

    <el-tooltip v-else effect="dark" content="修改标注" placement="top">
      <el-button text @click="editMark(data)">
        <AppIcon iconName="app-document-active" class="primary"></AppIcon>
      </el-button>
    </el-tooltip>

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
    <audio ref="audioPlayer" controls hidden="hidden"></audio>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { copyClick } from '@/utils/clipboard'
import EditContentDialog from '@/views/log/component/EditContentDialog.vue'
import EditMarkDialog from '@/views/log/component/EditMarkDialog.vue'
import { datetimeFormat } from '@/utils/time'
import applicationApi from '@/api/application'
import { useRoute } from 'vue-router'

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
  tts: Boolean,
  tts_type: String
})

const emit = defineEmits(['update:data'])

const audioPlayer = ref<HTMLAudioElement | null>(null)

const EditContentDialogRef = ref()
const EditMarkDialogRef = ref()

const buttonData = ref(props.data)
const loading = ref(false)

function editContent(data: any) {
  EditContentDialogRef.value.open(data)
}

function editMark(data: any) {
  EditMarkDialogRef.value.open(data)
}

const audioPlayerStatus = ref(false)

const playAnswerText = (text: string) => {
  if (!text) {
    text = '抱歉，没有查找到相关内容，请重新描述您的问题或提供更多信息。'
  }
  if (props.tts_type === 'BROWSER') {
    // 创建一个新的 SpeechSynthesisUtterance 实例
    const utterance = new SpeechSynthesisUtterance(text)
    // 调用浏览器的朗读功能
    window.speechSynthesis.speak(utterance)
  }
  if (props.tts_type === 'TTS') {
    audioPlayerStatus.value = true
    // 恢复上次暂停的播放
    if (audioPlayer.value?.src) {
      audioPlayer.value?.play()
      return
    }
    applicationApi
      .postTextToSpeech(id || (props.applicationId as string), { text: text }, loading)
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
  if (props.tts_type === 'TTS') {
    audioPlayerStatus.value = false
    audioPlayer.value?.pause()
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
