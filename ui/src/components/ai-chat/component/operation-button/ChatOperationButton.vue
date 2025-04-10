<template>
  <div class="chat-operation-button flex-between">
    <el-text type="info">
      <span class="ml-4" v-if="data.create_time">{{ datetimeFormat(data.create_time) }}</span>
    </el-text>

    <div>
      <!-- 语音播放 -->
      <span v-if="tts">
        <el-tooltip
          v-if="audioManage?.isPlaying()"
          effect="dark"
          :content="$t('chat.operation.pause')"
          placement="top"
        >
          <el-button
            type="primary"
            text
            :disabled="!data?.write_ed"
            @click="audioManage?.pause(true)"
          >
            <AppIcon iconName="app-video-pause"></AppIcon>
          </el-button>
        </el-tooltip>
        <el-tooltip effect="dark" :content="$t('chat.operation.play')" placement="top" v-else>
          <el-button
            text
            :disabled="!data?.write_ed"
            @click="
              () => {
                bus.emit('play:pause', props.data.record_id)
                audioManage?.play(props.data.answer_text, true, true)
              }
            "
          >
            <AppIcon iconName="app-video-play"></AppIcon>
          </el-button>
        </el-tooltip>

        <el-divider direction="vertical" />
      </span>
      <span v-if="type == 'ai-chat' || type == 'log'">
        <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
          <el-button text @click="copy(data)">
            <AppIcon iconName="app-copy"></AppIcon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip effect="dark" :content="$t('chat.operation.regeneration')" placement="top">
          <el-button :disabled="chat_loading" text @click="regeneration">
            <el-icon><RefreshRight /></el-icon>
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
      <div ref="audioCiontainer"></div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { nextTick, onMounted, ref, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import applicationApi from '@/api/application'
import { datetimeFormat } from '@/utils/time'
import { MsgError } from '@/utils/message'
import bus from '@/bus'
const copy = (data: any) => {
  try {
    const text = data.answer_text_list
      .map((item: Array<any>) => item.map((i) => i.content).join('\n'))
      .join('\n\n')
    copyClick(removeFormRander(text))
  } catch (e: any) {
    copyClick(removeFormRander(data?.answer_text.trim()))
  }
}
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
const buttonData = ref(props.data)
const loading = ref(false)

const audioList = ref<string[]>([])

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
   * 刚挂载
   */
  MOUNTED = 'MOUNTED',
  /**
   * 就绪
   */
  READY = 'READY',
  /**
   * 错误
   */
  ERROR = 'ERROR'
}
class AudioManage {
  textList: Array<string>
  statusList: Array<AudioStatus>
  audioList: Array<HTMLAudioElement | SpeechSynthesisUtterance>
  tryList: Array<number>
  ttsType: string
  root: Element
  is_end: boolean
  constructor(ttsType: string, root: HTMLDivElement) {
    this.textList = []
    this.audioList = []
    this.statusList = []
    this.tryList = []
    this.ttsType = ttsType
    this.root = root
    this.is_end = false
  }
  appendTextList(textList: Array<string>) {
    const newTextList = textList.slice(this.textList.length)
    // 没有新增段落
    if (newTextList.length <= 0) {
      return
    }
    newTextList.forEach((text, index) => {
      this.textList.push(text)
      this.statusList.push(AudioStatus.MOUNTED)
      this.tryList.push(1)
      index = this.textList.length - 1
      if (this.ttsType === 'TTS') {
        const audioElement: HTMLAudioElement = document.createElement('audio')
        audioElement.controls = false
        audioElement.hidden = true
        /**
         * 播放结束事件
         */
        audioElement.onended = () => {
          this.statusList[index] = AudioStatus.END
          // 如果所有的节点都播放结束
          if (this.statusList.every((item) => item === AudioStatus.END) && this.is_end) {
            this.statusList = this.statusList.map((item) => AudioStatus.READY)
            this.is_end = false
          } else {
            // next
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
                if (this.tryList[index] >= 3) {
                  MsgError(text)
                }
                this.statusList[index] = AudioStatus.ERROR
                throw ''
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
          // 如果所有的节点都播放结束
          if (this.statusList.every((item) => item === AudioStatus.END)) {
            this.statusList = this.statusList.map((item) => AudioStatus.READY)
          } else {
            // next
            this.play()
          }
        }
        speechSynthesisUtterance.onerror = (e) => {
          this.statusList[index] = AudioStatus.READY
        }

        this.statusList[index] = AudioStatus.READY
        this.audioList.push(speechSynthesisUtterance)
        this.play()
      }
    })
  }
  reTryError() {
    this.statusList.forEach((status, index) => {
      if (status === AudioStatus.ERROR && this.tryList[index] <= 3) {
        this.tryList[index]++
        const audioElement = this.audioList[index]
        if (audioElement instanceof HTMLAudioElement) {
          const text = this.textList[index]
          this.statusList[index] = AudioStatus.MOUNTED
          applicationApi
            .postTextToSpeech(
              (props.applicationId as string) || (id as string),
              { text: text },
              loading
            )
            .then(async (res: any) => {
              if (res.type === 'application/json') {
                const text = await res.text()
                if (this.tryList[index] >= 3) {
                  MsgError(text)
                }
                throw ''
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
      }
    })
  }
  isPlaying() {
    return this.statusList.some((item) => [AudioStatus.PLAY_INT].includes(item))
  }
  play(text?: string, is_end?: boolean, self?: boolean) {
    if (is_end) {
      this.is_end = true
    }
    if (self) {
      this.tryList = this.tryList.map((item) => 0)
    }
    if (text) {
      const textList = this.getTextList(text, is_end ? true : false)
      this.appendTextList(textList)
    }
    // 如果存在在阅读的元素则直接返回
    if (this.statusList.some((item) => [AudioStatus.PLAY_INT].includes(item))) {
      return
    }
    this.reTryError()

    // 需要播放的内容
    const index = this.statusList.findIndex((status) =>
      [AudioStatus.MOUNTED, AudioStatus.READY].includes(status)
    )
    if (index < 0 || this.statusList[index] === AudioStatus.MOUNTED) {
      return
    }

    const audioElement = this.audioList[index]

    if (audioElement instanceof HTMLAudioElement) {
      // 标签朗读
      try {
        this.statusList[index] = AudioStatus.PLAY_INT
        const play = audioElement.play()
        if (play instanceof Promise) {
          play.catch((e) => {
            this.statusList[index] = AudioStatus.READY
          })
        }
      } catch (e: any) {
        this.statusList[index] = AudioStatus.ERROR
      }
    } else {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume()
      } else {
        if (window.speechSynthesis.pending) {
          window.speechSynthesis.cancel()
        }
        speechSynthesis.speak(audioElement)
        this.statusList[index] = AudioStatus.PLAY_INT
      }
    }
  }
  pause(self?: boolean) {
    const index = this.statusList.findIndex((status) => status === AudioStatus.PLAY_INT)
    if (index < 0) {
      return
    }
    const audioElement = this.audioList[index]

    if (audioElement instanceof HTMLAudioElement) {
      if (this.statusList[index] === AudioStatus.PLAY_INT) {
        // 标签朗读
        this.statusList[index] = AudioStatus.READY
        audioElement.pause()
      }
    } else {
      this.statusList[index] = AudioStatus.READY
      if (self) {
        window.speechSynthesis.pause()
        nextTick(() => {
          if (!window.speechSynthesis.paused) {
            window.speechSynthesis.cancel()
          }
        })
      } else {
        window.speechSynthesis.cancel()
      }
    }
  }
  getTextList(text: string, is_end: boolean) {
    // 移除表单渲染器
    text = removeFormRander(text)
    // text 处理成纯文本
    text = markdownToPlainText(text)
    const split = smartSplit(
      text,
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
      if (props.tts && props.tts_autoplay) {
        if (audioManage.value) {
          audioManage.value.play(props.data.answer_text, data.is_end)
        }
      }
    }
  })
})
onBeforeUnmount(() => {
  bus.off('change:answer')
  bus.off('play:pause')
  if (audioManage.value) {
    audioManage.value.pause()
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel()
  }
})
</script>
<style lang="scss" scoped>
@media only screen and (max-width: 430px) {
  .chat-operation-button {
    display: block;
    text-align: right;
  }
}
</style>
