<template>
  <div ref="aiChatRef" class="ai-chat" :class="log ? 'chart-log' : ''">
    <div
      v-if="(inputFieldList.length > 0 || (debug && apiInputFieldList.length > 0)) && !log"
      class="mb-16"
      style="padding: 0 24px"
    >
      <el-card shadow="always" class="dialog-card">
        <div class="flex align-center cursor w-full" @click="showUserInput = !showUserInput">
          <el-icon class="mr-8 arrow-icon" :class="showUserInput ? 'rotate-90' : ''"
            ><CaretRight
          /></el-icon>
          用户输入
        </div>
        <el-collapse-transition>
          <div v-show="showUserInput" class="mt-16">
            <DynamicsForm
              :key="dynamicsFormRefresh"
              v-model="form_data"
              :model="form_data"
              label-position="left"
              require-asterisk-position="right"
              :render_data="inputFieldList"
              ref="dynamicsFormRef"
            />
            <DynamicsForm
              v-if="debug"
              v-model="api_form_data"
              :model="api_form_data"
              label-position="left"
              require-asterisk-position="right"
              :render_data="apiInputFieldList"
              ref="dynamicsFormRef2"
            />
          </div>
        </el-collapse-transition>
      </el-card>
    </div>
    <el-scrollbar ref="scrollDiv" @scroll="handleScrollTop">
      <div ref="dialogScrollbar" class="ai-chat__content p-24 chat-width">
        <div class="item-content mb-16" v-if="!props.available || (props.data?.prologue && !log)">
          <div class="avatar">
            <img v-if="data.avatar" :src="data.avatar" height="30px" />
            <LogoIcon v-else height="30px" />
          </div>

          <div class="content">
            <el-card shadow="always" class="dialog-card">
              <template v-for="(item, index) in prologueList" :key="index">
                <div
                  v-if="item.type === 'question'"
                  @click="quickProblemHandle(item.str)"
                  class="problem-button ellipsis-2 mb-8"
                  :class="log ? 'disabled' : 'cursor'"
                >
                  <el-icon>
                    <EditPen />
                  </el-icon>
                  {{ item.str }}
                </div>
                <MdPreview
                  v-else
                  class="mb-8"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="item.str"
                  noIconfont
                  no-mermaid
                />
              </template>
            </el-card>
          </div>
        </div>

        <template v-for="(item, index) in chatList" :key="index">
          <!-- 问题 -->
          <div class="item-content mb-16 lighter">
            <div class="avatar">
              <AppAvatar>
                <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
              </AppAvatar>
            </div>
            <div class="content">
              <div class="text break-all pre-wrap">
                {{ item.problem_text }}
              </div>
            </div>
          </div>
          <!-- 回答 -->
          <div class="item-content mb-16 lighter">
            <div class="avatar">
              <img v-if="data.avatar" :src="data.avatar" height="30px" />
              <LogoIcon v-else height="30px" />
            </div>

            <div class="content">
              <div v-if="!item.answer_text">
                <el-card
                  v-if="item.write_ed === undefined || item.write_ed === true"
                  shadow="always"
                  class="dialog-card"
                >
                  <MdRenderer
                    source=" 抱歉，没有查找到相关内容，请重新描述您的问题或提供更多信息。"
                  ></MdRenderer>
                  <!-- 知识来源 -->
                  <div v-if="showSource(item)">
                    <KnowledgeSource :data="item" :type="props.data.type" />
                  </div>
                </el-card>
                <el-card v-else-if="item.is_stop" shadow="always" class="dialog-card">
                  已停止回答
                </el-card>
                <el-card v-else shadow="always" class="dialog-card">
                  回答中 <span class="dotting"></span>
                </el-card>
              </div>

              <el-card v-else shadow="always" class="dialog-card">
                <MdRenderer
                  :source="item.answer_text"
                  :quick-problem-handle="quickProblemHandle"
                ></MdRenderer>
                <!-- 知识来源 -->
                <div v-if="showSource(item)">
                  <KnowledgeSource :data="item" :type="props.data.type" />
                </div>
              </el-card>
              <div class="flex-between mt-8" v-if="log">
                <LogOperationButton
                  v-model:data="chatList[index]"
                  :applicationId="appId"
                  :tts="props.data.tts_model_enable"
                  :tts_type="props.data.tts_type"
                />
              </div>

              <div class="flex-between mt-8" v-else>
                <div>
                  <el-button
                    type="primary"
                    v-if="item.is_stop && !item.write_ed"
                    @click="startChat(item)"
                    link
                    >继续
                  </el-button>
                  <el-button type="primary" v-else-if="!item.write_ed" @click="stopChat(item)" link
                    >停止回答
                  </el-button>
                </div>
              </div>
              <div v-if="item.write_ed && 500 != item.status" class="flex-between">
                <OperationButton
                  :tts="props.data.tts_model_enable"
                  :tts_type="props.data.tts_type"
                  :data="item"
                  :applicationId="appId"
                  :chatId="chartOpenId"
                  :chat_loading="loading"
                  @regeneration="regenerationChart(item)"
                />
              </div>
            </div>
          </div>
        </template>
      </div>
    </el-scrollbar>
    <div class="ai-chat__operate p-24" v-if="!log">
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
          <span v-if="props.data.stt_model_enable" class="flex align-center">
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
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, computed, watch, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import LogOperationButton from './LogOperationButton.vue'
import OperationButton from './OperationButton.vue'
import KnowledgeSource from './KnowledgeSource.vue'
import applicationApi from '@/api/application'
import logApi from '@/api/log'
import { ChatManagement, type chatType } from '@/api/type/application'
import { randomId } from '@/utils/utils'
import useStore from '@/stores'
import MdRenderer from '@/components/markdown/MdRenderer.vue'
import { isWorkFlow } from '@/utils/application'
import { debounce } from 'lodash'
import Recorder from 'recorder-core'
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine'
import { MsgWarning } from '@/utils/message'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormField } from '@/components/dynamics-form/type'
import { MsgAlert } from '@/utils/message'

defineOptions({ name: 'AiChat' })
const route = useRoute()
const {
  params: { accessToken, id },
  query: { mode }
} = route as any
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  appId: String, // 仅分享链接有
  log: Boolean,
  record: {
    type: Array<chatType[]>,
    default: () => []
  },
  // 应用是否可用
  available: {
    type: Boolean,
    default: true
  },
  chatId: {
    type: String,
    default: ''
  }, // 历史记录Id
  debug: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'scroll'])

const { application, common } = useStore()

const isMobile = computed(() => {
  return common.isMobile() || mode === 'embed'
})

const aiChatRef = ref()
const quickInputRef = ref()
const scrollDiv = ref()
const dialogScrollbar = ref()
const loading = ref(false)
const inputValue = ref<string>('')
const chartOpenId = ref('')
const chatList = ref<any[]>([])
const inputFieldList = ref<FormField[]>([])
const apiInputFieldList = ref<FormField[]>([])
const form_data = ref<any>({})
const api_form_data = ref<any>({})

const showUserInput = ref(true)
const recorderTime = ref(0)
const startRecorderTime = ref(false)
const recorderLoading = ref(false)

const isDisabledChart = computed(
  () => !(inputValue.value.trim() && (props.appId || props.data?.name))
)
const isMdArray = (val: string) => val.match(/^-\s.*/m)
const prologueList = computed(() => {
  const temp = props.available
    ? props.data?.prologue
    : '抱歉，当前正在维护，无法提供服务，请稍后再试！'
  const lines = temp?.split('\n')
  return lines
    .reduce((pre_array: Array<any>, current: string, index: number) => {
      const currentObj = isMdArray(current)
        ? {
            type: 'question',
            str: current.replace(/^-\s+/, ''),
            index: index
          }
        : {
            type: 'md',
            str: current,
            index: index
          }
      if (pre_array.length > 0) {
        const pre = pre_array[pre_array.length - 1]
        if (!isMdArray(current) && pre.type == 'md') {
          pre.str = [pre.str, current].join('\n')
          pre.index = index
          return pre_array
        } else {
          pre_array.push(currentObj)
        }
      } else {
        pre_array.push(currentObj)
      }
      return pre_array
    }, [])
    .sort((pre: any, next: any) => pre.index - next.index)
})

watch(
  () => props.chatId,
  (val) => {
    if (val && val !== 'new') {
      chartOpenId.value = val
    } else {
      chartOpenId.value = ''
    }
  },
  { deep: true }
)

// 用于刷新动态表单
const dynamicsFormRefresh = ref(0)
function handleInputFieldList() {
  dynamicsFormRefresh.value++
  // 给变量赋默认值, 最后一个对话记录的值
  const record = chatList.value[chatList.value.length - 1]
  let default_value: any = {}
  if (record) {
    record.execution_details[0].global_fields?.reduce((pre: any, next: any) => {
      pre[next.key] = next.value
      return pre
    }, default_value)
  }
  props.data.work_flow?.nodes
    ?.filter((v: any) => v.id === 'base-node')
    .map((v: any) => {
      inputFieldList.value = v.properties.input_field_list
        ? v.properties.input_field_list
            .filter((v: any) => v.assignment_method === 'user_input')
            .map((v: any) => {
              switch (v.type) {
                case 'input':
                  return {
                    field: v.variable,
                    input_type: 'TextInput',
                    label: v.name,
                    default_value: default_value[v.variable],
                    required: v.is_required
                  }
                case 'select':
                  return {
                    field: v.variable,
                    input_type: 'SingleSelect',
                    label: v.name,
                    default_value: default_value[v.variable],
                    required: v.is_required,
                    option_list: v.optionList.map((o: any) => {
                      return { key: o, value: o }
                    })
                  }
                case 'date':
                  return {
                    field: v.variable,
                    input_type: 'DatePicker',
                    label: v.name,
                    default_value: default_value[v.variable],
                    required: v.is_required,
                    attrs: {
                      format: 'YYYY-MM-DD HH:mm:ss',
                      'value-format': 'YYYY-MM-DD HH:mm:ss',
                      type: 'datetime'
                    }
                  }
                default:
                  break
              }
            })
        : []
      apiInputFieldList.value = v.properties.input_field_list
        ? v.properties.input_field_list
            .filter((v: any) => v.assignment_method === 'api_input')
            .map((v: any) => {
              switch (v.type) {
                case 'input':
                  return {
                    field: v.variable,
                    input_type: 'TextInput',
                    label: v.name,
                    default_value: default_value[v.variable],
                    required: v.is_required
                  }
                case 'select':
                  return {
                    field: v.variable,
                    input_type: 'SingleSelect',
                    label: v.name,
                    default_value: default_value[v.variable],
                    required: v.is_required,
                    option_list: v.optionList.map((o: any) => {
                      return { key: o, value: o }
                    })
                  }
                case 'date':
                  return {
                    field: v.variable,
                    input_type: 'DatePicker',
                    label: v.name,
                    default_value: default_value[v.variable],
                    required: v.is_required,
                    attrs: {
                      format: 'YYYY-MM-DD HH:mm:ss',
                      'value-format': 'YYYY-MM-DD HH:mm:ss',
                      type: 'datetime'
                    }
                  }
                default:
                  break
              }
            })
        : []
    })
}

watch(
  () => props.data,
  () => {
    chartOpenId.value = ''
    handleInputFieldList()
  },
  { deep: true }
)

watch(
  () => props.record,
  (value) => {
    chatList.value = value
    handleInputFieldList()
  },
  {
    immediate: true
  }
)

function showSource(row: any) {
  if (props.log) {
    return true
  } else if (row.write_ed && 500 !== row.status) {
    if (id || props.data?.show_source) {
      return true
    }
  } else {
    return false
  }
}

function quickProblemHandle(val: string) {
  if (!checkInputParam()) {
    return
  }
  if (!loading.value && props.data?.name) {
    handleDebounceClick(val)
  }
}

const handleDebounceClick = debounce((val) => {
  chatMessage(null, val)
}, 200)

function checkInputParam() {
  // 检查inputFieldList是否有未填写的字段
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if (inputFieldList.value[i].required && !form_data.value[inputFieldList.value[i].field]) {
      MsgWarning('请填写所有必填字段')
      return false
    }
  }
  // 浏览器query参数找到接口传参
  let msg = []
  for (let f of apiInputFieldList.value) {
    if (!api_form_data.value[f.field]) {
      api_form_data.value[f.field] = route.query[f.field]
    }
    if (f.required && !api_form_data.value[f.field]) {
      msg.push(f.field)
    }
  }
  if (msg.length > 0) {
    MsgWarning(`请在URL中填写参数 ${msg.join('、')}的值`)
    return false
  }
  return true
}

function sendChatHandle(event: any) {
  if (!checkInputParam()) {
    return
  }
  if (!event.ctrlKey) {
    // 如果没有按下组合键ctrl，则会阻止默认事件
    event.preventDefault()
    if (!isDisabledChart.value && !loading.value && !event.isComposing) {
      if (inputValue.value.trim()) {
        chatMessage()
      }
    }
  } else {
    // 如果同时按下ctrl+回车键，则会换行
    inputValue.value += '\n'
  }
}

const stopChat = (chat: chatType) => {
  ChatManagement.stop(chat.id)
}
const startChat = (chat: chatType) => {
  ChatManagement.write(chat.id)
}

/**
 * 对话
 */
function getChartOpenId(chat?: any) {
  loading.value = true
  const obj = props.data
  if (props.appId) {
    return applicationApi
      .getChatOpen(props.appId)
      .then((res) => {
        chartOpenId.value = res.data
        chatMessage(chat)
      })
      .catch((res) => {
        if (res.response.status === 403) {
          application.asyncAppAuthentication(accessToken).then(() => {
            getChartOpenId(chat)
          })
        } else {
          loading.value = false
          return Promise.reject(res)
        }
      })
  } else {
    if (isWorkFlow(obj.type)) {
      const submitObj = {
        work_flow: obj.work_flow
      }
      return applicationApi
        .postWorkflowChatOpen(submitObj)
        .then((res) => {
          chartOpenId.value = res.data
          chatMessage(chat)
        })
        .catch((res) => {
          loading.value = false
          return Promise.reject(res)
        })
    } else {
      return applicationApi
        .postChatOpen(obj)
        .then((res) => {
          chartOpenId.value = res.data
          chatMessage(chat)
        })
        .catch((res) => {
          loading.value = false
          return Promise.reject(res)
        })
    }
  }
}

/**
 * 获取一个递归函数,处理流式数据
 * @param chat    每一条对话记录
 * @param reader  流数据
 * @param stream  是否是流式数据
 */
const getWrite = (chat: any, reader: any, stream: boolean) => {
  let tempResult = ''
  /**
   *
   * @param done  是否结束
   * @param value 值
   */
  const write_stream = ({ done, value }: { done: boolean; value: any }) => {
    try {
      if (done) {
        ChatManagement.close(chat.id)
        return
      }
      const decoder = new TextDecoder('utf-8')
      let str = decoder.decode(value, { stream: true })
      // 这里解释一下 start 因为数据流返回流并不是按照后端chunk返回 我们希望得到的chunk是data:{xxx}\n\n 但是它获取到的可能是 data:{ -> xxx}\n\n 总而言之就是 fetch不能保证每个chunk都说以data:开始 \n\n结束
      tempResult += str
      const split = tempResult.match(/data:.*}\n\n/g)
      if (split) {
        str = split.join('')
        tempResult = tempResult.replace(str, '')
      } else {
        return reader.read().then(write_stream)
      }
      // 这里解释一下 end
      if (str && str.startsWith('data:')) {
        if (split) {
          for (const index in split) {
            const chunk = JSON?.parse(split[index].replace('data:', ''))
            chat.chat_id = chunk.chat_id
            chat.record_id = chunk.id
            const content = chunk?.content
            if (content) {
              ChatManagement.append(chat.id, content)
            }
            if (chunk.is_end) {
              // 流处理成功 返回成功回调
              return Promise.resolve()
            }
          }
        }
      }
    } catch (e) {
      return Promise.reject(e)
    }
    return reader.read().then(write_stream)
  }
  /**
   * 处理 json 响应
   * @param param0
   */
  const write_json = ({ done, value }: { done: boolean; value: any }) => {
    if (done) {
      const result_block = JSON.parse(tempResult)
      if (result_block.code === 500) {
        return Promise.reject(result_block.message)
      } else {
        if (result_block.content) {
          ChatManagement.append(chat.id, result_block.content)
        }
      }
      ChatManagement.close(chat.id)
      return
    }
    if (value) {
      const decoder = new TextDecoder('utf-8')
      tempResult += decoder.decode(value)
    }
    return reader.read().then(write_json)
  }
  return stream ? write_stream : write_json
}
const errorWrite = (chat: any, message?: string) => {
  ChatManagement.addChatRecord(chat, 50, loading)
  ChatManagement.write(chat.id)
  ChatManagement.append(chat.id, message || '抱歉，当前正在维护，无法提供服务，请稍后再试！')
  ChatManagement.updateStatus(chat.id, 500)
  ChatManagement.close(chat.id)
}

function chatMessage(chat?: any, problem?: string, re_chat?: boolean) {
  loading.value = true
  if (!chat) {
    chat = reactive({
      id: randomId(),
      problem_text: problem ? problem : inputValue.value.trim(),
      answer_text: '',
      buffer: [],
      write_ed: false,
      is_stop: false,
      record_id: '',
      vote_status: '-1',
      status: undefined
    })
    chatList.value.push(chat)
    ChatManagement.addChatRecord(chat, 50, loading)
    ChatManagement.write(chat.id)
    inputValue.value = ''
    nextTick(() => {
      // 将滚动条滚动到最下面
      scrollDiv.value.setScrollTop(getMaxHeight())
    })
  }
  if (!chartOpenId.value) {
    getChartOpenId(chat).catch(() => {
      errorWrite(chat)
    })
  } else {
    const obj = {
      message: chat.problem_text,
      re_chat: re_chat || false,
      form_data: { ...form_data.value, ...api_form_data.value }
    }
    // 对话
    applicationApi
      .postChatMessage(chartOpenId.value, obj)
      .then((response) => {
        if (response.status === 401) {
          application
            .asyncAppAuthentication(accessToken)
            .then(() => {
              chatMessage(chat, problem)
            })
            .catch(() => {
              errorWrite(chat)
            })
        } else if (response.status === 460) {
          return Promise.reject('无法识别用户身份')
        } else if (response.status === 461) {
          return Promise.reject('抱歉，您的提问已达到最大限制，请明天再来吧！')
        } else {
          nextTick(() => {
            // 将滚动条滚动到最下面
            scrollDiv.value.setScrollTop(getMaxHeight())
          })
          const reader = response.body.getReader()
          // 处理流数据
          const write = getWrite(
            chat,
            reader,
            response.headers.get('Content-Type') !== 'application/json'
          )
          return reader.read().then(write)
        }
      })
      .then(() => {
        if (props.chatId === 'new') {
          emit('refresh', chartOpenId.value)
        }
        quickInputRef.value.textareaStyle.height = '45px'
        return (id || props.data?.show_source) && getSourceDetail(chat)
      })
      .finally(() => {
        ChatManagement.close(chat.id)
      })
      .catch((e: any) => {
        errorWrite(chat, e + '')
      })
  }
}

function regenerationChart(item: chatType) {
  if (!checkInputParam()) {
    return
  }
  inputValue.value = item.problem_text
  if (!loading.value) {
    chatMessage(null, '', true)
  }
}

function getSourceDetail(row: any) {
  logApi.getRecordDetail(id || props.appId, row.chat_id, row.record_id, loading).then((res) => {
    const exclude_keys = ['answer_text', 'id']
    Object.keys(res.data).forEach((key) => {
      if (!exclude_keys.includes(key)) {
        row[key] = res.data[key]
      }
    })
  })
  return true
}

/**
 * 滚动条距离最上面的高度
 */
const scrollTop = ref(0)

const scorll = ref(true)

const getMaxHeight = () => {
  return dialogScrollbar.value!.scrollHeight
}
const handleScrollTop = ($event: any) => {
  scrollTop.value = $event.scrollTop
  if (
    dialogScrollbar.value.scrollHeight - (scrollTop.value + scrollDiv.value.wrapRef.offsetHeight) <=
    30
  ) {
    scorll.value = true
  } else {
    scorll.value = false
  }
  emit('scroll', { ...$event, dialogScrollbar: dialogScrollbar.value, scrollDiv: scrollDiv.value })
}

const handleScroll = () => {
  if (!props.log && scrollDiv.value) {
    // 内部高度小于外部高度 就需要出滚动条
    if (scrollDiv.value.wrapRef.offsetHeight < dialogScrollbar.value.scrollHeight) {
      // 如果当前滚动条距离最下面的距离在 规定距离 滚动条就跟随
      if (scorll.value) {
        scrollDiv.value.setScrollTop(getMaxHeight())
      }
    }
  }
}

// 定义响应式引用
const mediaRecorder = ref<any>(null)

const mediaRecorderStatus = ref(true)

// 开始录音
const startRecording = async () => {
  try {
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
    // console.error('无法获取音频权限：', error)
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
    applicationApi.postSpeechToText(props.data.id as string, formData, loading).then((response) => {
      console.log('上传成功:', response.data)
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

onMounted(() => {
  handleInputFieldList()
})

function setScrollBottom() {
  // 将滚动条滚动到最下面
  scrollDiv.value.setScrollTop(getMaxHeight())
}

watch(
  chatList,
  () => {
    handleScroll()
  },
  { deep: true, immediate: true }
)

onMounted(() => {
  setTimeout(() => {
    if (quickInputRef.value && mode === 'embed') {
      quickInputRef.value.textarea.style.height = '0'
    }
  }, 1800)
})

defineExpose({
  setScrollBottom
})
</script>
<style lang="scss" scoped>
.ai-chat {
  --padding-left: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  color: var(--app-text-color);
  box-sizing: border-box;

  &__content {
    padding-top: 0;
    box-sizing: border-box;

    .avatar {
      float: left;
    }

    .content {
      padding-left: var(--padding-left);

      :deep(ol) {
        margin-left: 16px !important;
      }
    }

    .text {
      padding: 6px 0;
    }

    .problem-button {
      width: 100%;
      border: none;
      border-radius: 8px;
      background: var(--app-layout-bg-color);
      height: 46px;
      padding: 0 12px;
      line-height: 46px;
      box-sizing: border-box;
      color: var(--el-text-color-regular);
      -webkit-line-clamp: 1;
      word-break: break-all;

      &:hover {
        background: var(--el-color-primary-light-9);
      }

      &.disabled {
        &:hover {
          background: var(--app-layout-bg-color);
        }
      }

      :deep(.el-icon) {
        color: var(--el-color-primary);
      }
    }
  }

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

      :deep(.el-textarea__inner) {
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

        :deep(.el-loading-spinner) {
          margin-top: -15px;

          .circular {
            width: 31px;
            height: 31px;
          }
        }
      }
    }
  }

  .dialog-card {
    border: none;
    border-radius: 8px;
    box-sizing: border-box;
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
