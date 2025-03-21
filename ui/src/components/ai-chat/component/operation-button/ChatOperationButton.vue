<template>
  <div class="chat-operation-button flex-between">
    <el-text type="info">
      <span class="ml-4">{{ datetimeFormat(data.create_time) }}</span>
    </el-text>

    <div>
      <!-- 语音播放 -->
      <span v-if="tts">
        <el-tooltip
          effect="dark"
          :content="$t('chat.operation.play')"
          placement="top"
          v-if="!audioPlayerStatus"
        >
          <el-button
            text
            :disabled="!data?.write_ed"
            @click="
              () => {
                bus.emit('play:pause', props.data.record_id)
                audioManage?.play(props.data.answer_text, true)
              }
            "
          >
            <AppIcon iconName="app-video-play"></AppIcon>
          </el-button>
        </el-tooltip>
        <el-tooltip v-else effect="dark" :content="$t('chat.operation.pause')" placement="top">
          <el-button
            type="primary"
            text
            :disabled="!data?.write_ed"
            @click="audioManage?.pause.bind(audioManage)"
          >
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
    <div ref="audioCiontainer"></div>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import applicationApi from '@/api/application'
import { datetimeFormat } from '@/utils/time'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'
import bus from '@/bus'

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
const audioCiontainer = ref<HTMLDivElement>()
const audioPlayerStatus = ref(false)
const buttonData = ref(props.data)
const loading = ref(false)
const utterance = ref<SpeechSynthesisUtterance | null>(null)
const audioList = ref<string[]>([])
const currentAudioIndex = ref(0)
const demo = computed(() => {
  return props.data.answer_text
})
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
  return text.replace(/<form_rander>[\s\S]*?<\/form_rander>/g, '').trim()
}
function getKey(keys: Array<number>, index: number) {
  // 从后往前查找第一个小于等于index的键
  for (let i = keys.length - 1; i >= 0; i--) {
    if (keys[i] <= index) {
      return keys[i]
    }
  }
  return 0
}
function smartSplit(
  str: string,
  minLengthConfig: any = {
    0: 10,
    1: 25,
    3: 50,
    5: 100
  },
  is_end = false
) {
  // 匹配中文逗号/句号，且后面至少还有20个字符（含任何字符，包括换行）
  const regex = /([。？\n])|(<audio[^>]*><\/audio>)/g
  // 拆分并保留分隔符
  const parts = str.split(regex)
  const result = []
  const keys = Object.keys(minLengthConfig).map(Number)
  let minLength = minLengthConfig[0]
  let temp_str = ''
  for (let i = 0; i < parts.length; i++) {
    const content = parts[i]
    if (content == undefined) {
      continue
    }
    if (/^<audio[^>]*><\/audio>$/.test(content)) {
      if (temp_str.length > 0) {
        result.push(temp_str)
        temp_str = ''
      }
      result.push(content)
      continue
    }
    temp_str += parts[i]
    if (temp_str.length > minLength && /[。？\n]$/.test(temp_str)) {
      minLength = minLengthConfig[getKey(keys, i)]
      result.push(temp_str)
      temp_str = ''
    }
  }
  if (temp_str.length > 0 && is_end) {
    result.push(temp_str)
  }
  return result
}

enum AudioStatus {
  /**
   * 结束
   */
  END = 'END',
  /**
   * 播放中
   */
  PLAY_INT = 'PLAY_INT',
  /**
   * 手动暂停
   */
  PAUSE = 'PAUSE',
  /**
   * 等待 程序流式输出新分段未出来
   */
  WAIT = 'WAIT',
  /**
   * 刚挂载
   */
  MOUNTED = 'MOUNTED',
  /**
   * 就绪
   */
  READY = 'READY',

  ERROR = 'ERROR'
}
class AudioManage {
  textList: Array<string>
  statusList: Array<AudioStatus>
  audioList: Array<HTMLAudioElement | SpeechSynthesisUtterance>
  ttsType: string
  root: Element
  constructor(ttsType: string, root: HTMLDivElement) {
    this.textList = []
    this.audioList = []
    this.statusList = []
    this.ttsType = ttsType
    this.root = root
  }
  appendTextList(textList: Array<string>) {
    const newTextList = textList.slice(this.textList.length)
    // 没有新增段落
    if (newTextList.length <= 0) {
      return
    }
    this.statusList.forEach((status, index) => {
      if (status === AudioStatus.ERROR) {
        const audioElement = this.audioList[index]
        if (audioElement instanceof HTMLAudioElement) {
          const text = this.textList[index]
          applicationApi
            .postTextToSpeech(
              (props.applicationId as string) || (id as string),
              { text: text },
              loading
            )
            .then(async (res: any) => {
              if (res.type === 'application/json') {
                const text = await res.text()
                MsgError(text)
                this.statusList[index] = AudioStatus.ERROR
                return
              }
              // 假设我们有一个 MP3 文件的字节数组
              // 创建 Blob 对象
              const blob = new Blob([res], { type: 'audio/mp3' })

              // 创建对象 URL
              const url = URL.createObjectURL(blob)
              audioElement.src = url
              this.statusList[index] = AudioStatus.READY
              this.play()
            })
            .catch((err) => {
              console.log('err: ', err)
              this.statusList[index] = AudioStatus.ERROR
            })
        }
      }
    })
    newTextList.forEach((text, index) => {
      this.textList.push(text)
      this.statusList.push(AudioStatus.MOUNTED)
      index = this.textList.length - 1
      if (this.ttsType === 'TTS') {
        const audioElement: HTMLAudioElement = document.createElement('audio')
        audioElement.controls = true
        audioElement.hidden = true
        /**
         * 播放结束事件
         */
        audioElement.onended = () => {
          this.statusList[index] = AudioStatus.END
          if (this.statusList.every((item) => item === AudioStatus.END)) {
            this.statusList = this.statusList.map((item) => AudioStatus.READY)
          } else {
            this.play()
          }
        }
        this.root.appendChild(audioElement)
        if (/^<audio[^>]*><\/audio>$/.test(text)) {
          audioElement.src = text.match(/src="([^"]*)"/)?.[1] || ''
          this.statusList[index] = AudioStatus.READY
        } else {
          applicationApi
            .postTextToSpeech(
              (props.applicationId as string) || (id as string),
              { text: text },
              loading
            )
            .then(async (res: any) => {
              if (res.type === 'application/json') {
                const text = await res.text()
                MsgError(text)
                this.statusList[index] = AudioStatus.ERROR
                this.play()
                return
              }
              // 假设我们有一个 MP3 文件的字节数组
              // 创建 Blob 对象
              const blob = new Blob([res], { type: 'audio/mp3' })

              // 创建对象 URL
              const url = URL.createObjectURL(blob)
              audioElement.src = url
              this.statusList[index] = AudioStatus.READY
              this.play()
            })
            .catch((err) => {
              console.log('err: ', err)
              this.statusList[index] = AudioStatus.ERROR
              this.play()
            })
        }

        this.audioList.push(audioElement)
      } else {
        const speechSynthesisUtterance: SpeechSynthesisUtterance = new SpeechSynthesisUtterance(
          text
        )
        speechSynthesisUtterance.onend = () => {
          this.statusList[index] = AudioStatus.END
        }
        this.statusList[index] = AudioStatus.READY
        this.audioList.push(speechSynthesisUtterance)
      }
    })
  }
  play(text?: string, is_end?: boolean) {
    if (text) {
      const textList = this.getTextList(text, is_end ? true : false)
      this.appendTextList(textList)
    }

    // 如果存在在阅读的元素则直接返回
    if (this.statusList.some((item) => [AudioStatus.PAUSE, AudioStatus.PLAY_INT].includes(item))) {
      return
    }
    // 需要播放的内容
    const index = this.statusList.findIndex((status) =>
      [AudioStatus.READY, AudioStatus.MOUNTED].includes(status)
    )

    if (index < 0 || this.statusList[index] === AudioStatus.MOUNTED) {
      return
    }
    console.log(index, this.audioList, this.statusList)
    const audioElement = this.audioList[index]
    if (audioElement instanceof SpeechSynthesisUtterance) {
      this.statusList[index] = AudioStatus.PLAY_INT
      // 调用浏览器的朗读功能
      window.speechSynthesis.speak(audioElement)
    } else {
      // 标签朗读
      this.statusList[index] = AudioStatus.PLAY_INT
      audioElement.play()
    }
  }
  pause() {
    const index = this.statusList.findIndex((status) => status === AudioStatus.PLAY_INT)
    if (index < 0) {
      return
    }
    const audioElement = this.audioList[index]
    if (audioElement instanceof SpeechSynthesisUtterance) {
      this.statusList[index] = AudioStatus.PAUSE
      // 调用浏览器的朗读功能
      window.speechSynthesis.pause()
    } else {
      if (this.statusList[index] === AudioStatus.PLAY_INT) {
        // 标签朗读
        this.statusList[index] = AudioStatus.PAUSE
        audioElement.pause()
      }
    }
  }
  getTextList(text: string, is_end: boolean) {
    // 移除表单渲染器
    text = removeFormRander(text)
    // text 处理成纯文本
    text = markdownToPlainText(text)
    const split = smartSplit(
      props.data.answer_text,
      {
        0: 20,
        1: 50,
        5: 100
      },
      is_end
    )
    return split
  }
}
const audioManage = ref<AudioManage>()
onMounted(() => {
  if (audioCiontainer.value) {
    audioManage.value = new AudioManage(props.tts_type, audioCiontainer.value)
  }
  bus.on('play:pause', (record_id: string) => {
    if (record_id !== props.data.record_id) {
      if (audioManage.value) {
        audioManage.value?.pause()
      }
    }
  })

  bus.on('change:answer', (data: any) => {
    const record_id = data.record_id
    bus.emit('play:pause', record_id)
    if (props.data.record_id == record_id) {
      if (props.tts) {
        if (audioManage.value) {
          audioManage.value.play(props.data.answer_text)
        }
      }
    }
  })
})
</script>
<style lang="scss" scoped>
@media only screen and (max-width: 430px) {
  .chat-operation-button {
    display: block;
  }
}
</style>
