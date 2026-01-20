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
            <AppIcon class="color-secondary" iconName="app-video-pause"></AppIcon>
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
            <AppIcon class="color-secondary" iconName="app-video-play"></AppIcon>
          </el-button>
        </el-tooltip>

        <el-divider direction="vertical" />
      </span>
      <span v-if="type == 'ai-chat' || type == 'log'">
        <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
          <el-button text @click="copy(data)">
            <AppIcon class="color-secondary" iconName="app-copy"></AppIcon>
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
          v-if="buttonData?.vote_status === '-1' && mode === 'mobile'"
          effect="dark"
          :content="$t('chat.operation.like')"
          placement="top"
        >
          <el-button text :disabled="loading" @click="mobileVoteReasonHandler('0')">
            <AppIcon class="color-secondary" iconName="app-like"></AppIcon>
          </el-button>
        </el-tooltip>

        <el-popover
          ref="likePopoverRef"
          trigger="click"
          placement="bottom-start"
          :width="360"
          popper-class="vote-popover"
          v-if="buttonData?.vote_status === '-1' && mode !== 'mobile'"
        >
          <template #reference>
            <span>
              <el-tooltip effect="dark" :content="$t('chat.operation.like')" placement="top">
                <el-button text :disabled="loading">
                  <AppIcon class="color-secondary" iconName="app-like"></AppIcon>
                </el-button>
              </el-tooltip>
            </span>
          </template>
          <VoteReasonContent
            vote-type="0"
            :chat-id="props.chatId"
            :record-id="props.data.record_id"
            @success="handleVoteSuccess"
            @close="closePopover"
          >
          </VoteReasonContent>
        </el-popover>

        <el-tooltip
          effect="dark"
          :content="$t('chat.operation.cancelLike')"
          placement="top"
          v-if="buttonData?.vote_status === '0'"
        >
          <el-button text @click="cancelVoteHandle('-1')" :disabled="loading">
            <AppIcon class="color-secondary" iconName="app-like-color"></AppIcon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" v-if="buttonData?.vote_status === '-1'" />
        <el-tooltip
          v-if="buttonData?.vote_status === '-1' && mode === 'mobile'"
          effect="dark"
          :content="$t('chat.operation.oppose')"
          placement="top"
        >
          <el-button text :disabled="loading" @click="mobileVoteReasonHandler('1')">
            <AppIcon class="color-secondary" iconName="app-oppose"></AppIcon>
          </el-button>
        </el-tooltip>
        <el-popover
          ref="opposePopoverRef"
          trigger="click"
          placement="bottom-start"
          :width="360"
          popper-class="vote-popover"
          v-if="buttonData?.vote_status === '-1' && mode !== 'mobile'"
        >
          <template #reference>
            <span>
              <el-tooltip effect="dark" :content="$t('chat.operation.oppose')" placement="top">
                <el-button text :disabled="loading">
                  <AppIcon class="color-secondary" iconName="app-oppose"></AppIcon>
                </el-button>
              </el-tooltip>
            </span>
          </template>
          <VoteReasonContent
            vote-type="1"
            :chat-id="props.chatId"
            :record-id="props.data.record_id"
            @success="handleVoteSuccess"
            @close="closePopover"
          >
          </VoteReasonContent>
        </el-popover>
        <el-tooltip
          effect="dark"
          :content="$t('chat.operation.cancelOppose')"
          placement="top"
          v-if="buttonData?.vote_status === '1'"
        >
          <el-button text @click="cancelVoteHandle('-1')" :disabled="loading">
            <AppIcon class="color-secondary" iconName="app-oppose-color"></AppIcon>
          </el-button>
        </el-tooltip>
      </span>
      <div ref="audioCiontainer"></div>
    </div>
    <MobileVoteReasonDrawer
      ref="mobileVoteReasonDrawerRef"
      :chat-id="props.chatId"
      :record-id="props.data.record_id"
      @success="handleVoteSuccess"
    />
  </div>
</template>
<script setup lang="ts">
import { nextTick, onMounted, ref, onBeforeUnmount, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import applicationApi from '@/api/application/application'
import chatAPI from '@/api/chat/chat'
import { datetimeFormat } from '@/utils/time'
import { MsgError } from '@/utils/message'
import VoteReasonContent from '@/components/ai-chat/component/operation-button/VoteReasonContent.vue'
import MobileVoteReasonDrawer from '@/components/ai-chat/component/operation-button/MobileVoteReasonDrawer.vue'
import bus from '@/bus'

const route = useRoute()
const {
  params: { id },
  query: { mode },
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
    type: 'ai-chat',
  },
)

const emit = defineEmits(['update:data', 'regeneration'])

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

const likePopoverRef = ref()
const opposePopoverRef = ref()
const closePopover = () => {
  likePopoverRef.value.hide()
  opposePopoverRef.value.hide()
}
const mobileVoteReasonDrawerRef = ref<InstanceType<typeof MobileVoteReasonDrawer> | null>(null)
const mobileVoteReasonHandler = (voteStatus: string) => {
  if (mobileVoteReasonDrawerRef.value) {
    mobileVoteReasonDrawerRef.value.open(voteStatus)
  }
}

const audioPlayer = ref<HTMLAudioElement[] | null>([])
const audioCiontainer = ref<HTMLDivElement>()
const buttonData = ref(props.data)
const loading = ref(false)
const audioList = ref<string[]>([])

function regeneration() {
  emit('regeneration')
}

function handleVoteSuccess(voteStatus: string) {
  buttonData.value['vote_status'] = voteStatus
  emit('update:data', buttonData.value)
  if (mode !== 'mobile') {
    closePopover()
  }
}

function cancelVoteHandle(val: string) {
  chatAPI.vote(props.chatId, props.data.record_id, val, undefined, '', loading).then(() => {
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
      // 移除video标签
      .replace(/<video>[\s\S]*?<\/video>/g, '')
      // 移除html标签
      .replace(/<[^>]+>/g, '')
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
    5: 100,
  },
  is_end = false,
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
  ERROR = 'ERROR',
}
const getTextToSpeechAPI = () => {
  if (props.type === 'ai-chat') {
    return (application_id?: string, data?: any, loading?: Ref<boolean>) => {
      return chatAPI.textToSpeech(data, loading)
    }
  } else {
    return applicationApi.postTextToSpeech
  }
}
const textToSpeechAPI = getTextToSpeechAPI()
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
      return 0
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
          textToSpeechAPI(
            (props.applicationId as string) || (id as string),
            { text: text },
            loading,
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
          text,
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
          textToSpeechAPI(
            (props.applicationId as string) || (id as string),
            { text: text },
            loading,
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
      if (this.appendTextList(textList) !== 0) {
        // 没有新增段落
        return
      }
    }
    // 如果存在在阅读的元素则直接返回
    if (this.statusList.some((item) => [AudioStatus.PLAY_INT].includes(item))) {
      return
    }
    this.reTryError()

    // 需要播放的内容
    const index = this.statusList.findIndex((status) =>
      [AudioStatus.MOUNTED, AudioStatus.READY].includes(status),
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
      if (window.speechSynthesis.paused && self) {
        window.speechSynthesis.resume()
        this.statusList[index] = AudioStatus.PLAY_INT
      } else {
        // 如果不是暂停状态，取消当前播放并重新开始
        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel()
        }
        // 等待取消完成后重新播放
        setTimeout(() => {
          if (speechSynthesis.speaking) {
            return
          }
          speechSynthesis.speak(audioElement)
          this.statusList[index] = AudioStatus.PLAY_INT
        }, 500)
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
        5: 100,
      },
      is_end,
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
<style lang="scss">
@media only screen and (max-width: 430px) {
  .chat-operation-button {
    display: block;
    text-align: right;
  }
}
.vote-popover {
  padding: 20px 24px !important;
  color: var(--el-text-color-primary) !important;
}
</style>
