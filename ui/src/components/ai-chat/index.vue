<template>
  <div
    ref="aiChatRef"
    class="ai-chat"
    :class="type"
    :style="{
      height: firsUserInput ? '100%' : undefined,
    }"
  >
    <div
      v-show="showUserInputContent"
      :class="firsUserInput ? 'firstUserInput' : 'popperUserInput'"
    >
      <UserForm
        v-model:api_form_data="api_form_data"
        v-model:form_data="form_data"
        :application="applicationDetails"
        :type="type"
        :first="firsUserInput"
        @confirm="UserFormConfirm"
        @cancel="UserFormCancel"
        ref="userFormRef"
      >
      </UserForm>
    </div>
    <template v-if="!(isUserInput || isAPIInput) || !firsUserInput || type === 'log'">
      <el-scrollbar ref="scrollDiv" @scroll="handleScrollTop">
        <div ref="dialogScrollbar" class="ai-chat__content p-16" id="chatListId">
          <PrologueContent
            :type="type"
            :application="applicationDetails"
            :available="available"
            :send-message="sendMessage"
          ></PrologueContent>

          <template v-for="(item, index) in chatList" :key="index">
            <!-- 问题 -->
            <QuestionContent
              :type="type"
              :application="applicationDetails"
              :chat-record="item"
            ></QuestionContent>
            <!-- 回答 -->
            <AnswerContent
              :application="applicationDetails"
              :loading="loading"
              v-model:chat-record="chatList[index]"
              :type="type"
              :send-message="sendMessage"
              :chat-management="ChatManagement"
              :executionIsRightPanel="props.executionIsRightPanel"
              @open-execution-detail="emit('openExecutionDetail', chatList[index])"
              @openParagraph="emit('openParagraph', chatList[index])"
              @openParagraphDocument="
                (val: any) => emit('openParagraphDocument', chatList[index], val)
              "
            ></AnswerContent>
          </template>
          <TransitionContent
            v-if="transcribing"
            :text="t('chat.inputPlaceholder.recorderLoading')"
            :type="type"
            :application="applicationDetails"
          >
          </TransitionContent>
        </div>
      </el-scrollbar>
      <div style="position: relative">
        <!-- 置底按钮 -->
        <el-button v-if="isBottom" circle class="back-bottom-button" @click="setScrollBottom">
          <el-icon><ArrowDownBold /></el-icon>
        </el-button>
        <ChatInputOperate
          :app-id="appId"
          :application-details="applicationDetails"
          :is-mobile="isMobile"
          :type="type"
          :send-message="sendMessage"
          :open-chat-id="openChatId"
          :validate="validate"
          :chat-management="ChatManagement"
          v-model:chat-id="chartOpenId"
          v-model:loading="loading"
          v-model:show-user-input="showUserInput"
          v-if="type !== 'log'"
        >
          <template #userInput>
            <el-button
              v-if="isUserInput || isAPIInput"
              class="user-input-button mb-8"
              @click="toggleUserInput"
            >
              <AppIcon iconName="app-edit" :size="16" class="mr-4"></AppIcon>
              <span class="ellipsis">
                {{ userInputTitle || $t('chat.userInput') }}
              </span>
            </el-button>
          </template>
        </ChatInputOperate>
      </div>
      <Control></Control>
    </template>
  </div>
</template>
<script setup lang="ts">
import {
  type Ref,
  ref,
  nextTick,
  computed,
  watch,
  reactive,
  onMounted,
  onBeforeUnmount,
  provide,
  onBeforeMount,
} from 'vue'
import { useRoute } from 'vue-router'
import applicationApi from '@/api/application/application'
import chatAPI from '@/api/chat/chat'
import SystemResourceManagementApplicationAPI from '@/api/system-resource-management/application.ts'
import syetrmResourceManagementChatLogApi from '@/api/system-resource-management/chat-log'
import chatLogApi from '@/api/application/chat-log'
import { ChatManagement, type chatType } from '@/api/type/application'
import { randomId } from '@/utils/common'
import useStore from '@/stores'
import { debounce } from 'lodash'
import AnswerContent from '@/components/ai-chat/component/answer-content/index.vue'
import QuestionContent from '@/components/ai-chat/component/question-content/index.vue'
import TransitionContent from '@/components/ai-chat/component/transition-content/index.vue'
import ChatInputOperate from '@/components/ai-chat/component/chat-input-operate/index.vue'
import PrologueContent from '@/components/ai-chat/component/prologue-content/index.vue'
import UserForm from '@/components/ai-chat/component/user-form/index.vue'
import Control from '@/components/ai-chat/component/control/index.vue'
import { t } from '@/locales'
import bus from '@/bus'
provide('upload', (file: any, loading?: Ref<boolean>) => {
  return props.type === 'debug-ai-chat'
    ? applicationApi.postUploadFile(file, 'TEMPORARY_120_MINUTE', 'TEMPORARY_120_MINUTE', loading)
    : chatAPI.postUploadFile(file, chartOpenId.value, 'CHAT', loading)
})
const transcribing = ref<boolean>(false)
defineOptions({ name: 'AiChat' })
const route = useRoute()
const {
  params: { accessToken, id },
  query: { mode },
} = route as any
const props = withDefaults(
  defineProps<{
    applicationDetails: any
    type?: 'log' | 'ai-chat' | 'debug-ai-chat'
    appId?: string
    record?: Array<chatType>
    available?: boolean
    chatId?: string
    executionIsRightPanel?: boolean
  }>(),
  {
    applicationDetails: () => ({}),
    available: true,
    type: 'ai-chat',
  },
)
const emit = defineEmits([
  'refresh',
  'scroll',
  'openExecutionDetail',
  'openParagraph',
  'openParagraphDocument',
])
const { application, common, chatUser } = useStore()
const isMobile = computed(() => {
  return common.isMobile() || mode === 'embed' || mode === 'mobile'
})
const aiChatRef = ref()
const scrollDiv = ref()
const dialogScrollbar = ref()
const loading = ref(false)
const inputValue = ref<string>('')
const chartOpenId = ref<string>('')
const chatList = ref<any[]>([])
const form_data = ref<any>({})
const api_form_data = ref<any>({})
const userFormRef = ref<InstanceType<typeof UserForm>>()
// 用户输入
const firsUserInput = ref(false)
const showUserInput = ref(false)

// 初始表单数据（用于恢复）
const initialFormData = ref({})
const initialApiFormData = ref({})

const isUserInput = computed(
  () =>
    props.applicationDetails.work_flow?.nodes?.filter((v: any) => v.id === 'base-node')[0]
      ?.properties.user_input_field_list.length > 0,
)

const userInputTitle = computed(
  () =>
    props.applicationDetails.work_flow?.nodes?.filter((v: any) => v.id === 'base-node')[0]
      ?.properties?.user_input_config?.title,
)
const isAPIInput = computed(
  () =>
    props.type === 'debug-ai-chat' &&
    props.applicationDetails.work_flow?.nodes?.filter((v: any) => v.id === 'base-node')[0]
      .properties.api_input_field_list.length > 0,
)
const showUserInputContent = computed(() => {
  return (
    (((isUserInput.value || isAPIInput.value) && firsUserInput.value) || showUserInput.value) &&
    props.type !== 'log'
  )
})
watch(
  () => props.chatId,
  (val) => {
    if (val && val !== 'new') {
      chartOpenId.value = val
      firsUserInput.value = false
    } else {
      chartOpenId.value = ''
      if (isUserInput.value) {
        firsUserInput.value = true
      } else if (props.type == 'debug-ai-chat' && isAPIInput.value) {
        firsUserInput.value = true
      }
    }
  },
  { deep: true, immediate: true },
)

watch(
  () => props.applicationDetails,
  () => {
    chartOpenId.value = ''
  },
  { deep: true },
)

watch(
  () => props.record,
  (value) => {
    chatList.value = value ? value : []
  },
  {
    immediate: true,
  },
)

const toggleUserInput = () => {
  showUserInput.value = !showUserInput.value
  if (showUserInput.value) {
    // 保存当前数据作为初始数据（用于可能的恢复）
    initialFormData.value = JSON.parse(JSON.stringify(form_data.value))
    initialApiFormData.value = JSON.parse(JSON.stringify(api_form_data.value))
  }
}

function UserFormConfirm() {
  firsUserInput.value = false
  showUserInput.value = false
}
function UserFormCancel() {
  // 恢复初始数据
  form_data.value = JSON.parse(JSON.stringify(initialFormData.value))
  api_form_data.value = JSON.parse(JSON.stringify(initialApiFormData.value))
  userFormRef.value?.render(form_data.value)
  showUserInput.value = false
}

const validate = () => {
  return userFormRef.value?.validate() || Promise.reject(false)
}

function sendMessage(val: string, other_params_data?: any, chat?: chatType): Promise<boolean> {
  if (isUserInput.value) {
    if (userFormRef.value) {
      return userFormRef.value
        ?.validate()
        .then((ok) => {
          const userFormData = accessToken
            ? JSON.parse(localStorage.getItem(`${accessToken}userForm`) || '{}')
            : {}
          const newData = Object.keys(form_data.value).reduce((result: any, key: string) => {
            result[key] = Object.prototype.hasOwnProperty.call(userFormData, key)
              ? userFormData[key]
              : form_data.value[key]
            return result
          }, {})
          if (accessToken) {
            localStorage.setItem(`${accessToken}userForm`, JSON.stringify(newData))
          }

          showUserInput.value = false

          if (!loading.value && props.applicationDetails?.name) {
            handleDebounceClick(val, other_params_data, chat)
            return true
          }
          throw 'err: no send'
        })
        .catch((e) => {
          if (isAPIInput.value && props.type !== 'debug-ai-chat') {
            showUserInput.value = false
          } else {
            showUserInput.value = true
          }

          return false
        })
    } else {
      return Promise.reject(false)
    }
  } else {
    showUserInput.value = false
    if (!loading.value && props.applicationDetails?.name) {
      handleDebounceClick(val, other_params_data, chat)
      return Promise.resolve(true)
    }
    return Promise.reject(false)
  }
}

const handleDebounceClick = debounce((val, other_params_data?: any, chat?: chatType) => {
  chatMessage(chat, val, false, other_params_data)
}, 200)

/**
 * 打开对话id
 */
const openChatId: () => Promise<string> = () => {
  const obj = props.applicationDetails
  return getOpenChatAPI()(obj.id)
    .then((res) => {
      chartOpenId.value = res.data
      return res.data
    })
    .catch((res) => {
      return Promise.reject(res)
    })
}

const getChatMessageAPI = () => {
  if (props.type === 'debug-ai-chat') {
    return applicationApi.chat
  } else {
    return chatAPI.chat
  }
}
const getOpenChatAPI = () => {
  if (props.type === 'debug-ai-chat') {
    if (route.path.includes('resource-management')) {
      return SystemResourceManagementApplicationAPI.open
    } else {
      return applicationApi.open
    }
  } else {
    return (a?: string, loading?: Ref<boolean>) => {
      return chatAPI.open(loading)
    }
  }
}

const getChatRecordDetailsAPI = (row: any) => {
  if (row.record_id) {
    if (props.type === 'debug-ai-chat') {
      if (route.path.includes('resource-management')) {
        return syetrmResourceManagementChatLogApi.getChatRecordDetails(
          id || props.appId,
          row.chat_id,
          row.record_id,
          loading,
        )
      } else {
        return chatLogApi.getChatRecordDetails(
          id || props.appId,
          row.chat_id,
          row.record_id,
          loading,
        )
      }
    } else {
      return chatAPI.getChatRecord(row.chat_id, row.record_id, loading)
    }
  }
  return Promise.reject('404')
}
/**
 * 获取对话详情
 * @param row
 */
function getSourceDetail(row: any) {
  return getChatRecordDetailsAPI(row).then((res) => {
    const exclude_keys = ['answer_text', 'id', 'answer_text_list']
    Object.keys(res.data).forEach((key) => {
      if (!exclude_keys.includes(key)) {
        row[key] = res.data[key]
      }
    })
  })
}
/**
 * 对话
 */
function getChartOpenId(chat?: any, problem?: string, re_chat?: boolean, other_params_data?: any) {
  return openChatId().then(() => {
    chatMessage(chat, problem, re_chat, other_params_data)
  })
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
            chat.record_id = chunk.chat_record_id
            if (!chunk.is_end) {
              ChatManagement.appendChunk(chat.id, chunk)
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
  ChatManagement.append(chat.id, message || t('chat.tip.error500Message'))
  ChatManagement.updateStatus(chat.id, 500)
  ChatManagement.close(chat.id)
}
// 保存上传文件列表

function chatMessage(chat?: any, problem?: string, re_chat?: boolean, other_params_data?: any) {
  loading.value = true
  if (!chat) {
    chat = reactive({
      id: randomId(),
      problem_text: problem ? problem : inputValue.value.trim(),
      answer_text: '',
      answer_text_list: [[]],
      buffer: [],
      reasoning_content: '',
      reasoning_content_buffer: [],
      write_ed: false,
      is_stop: false,
      record_id: '',
      chat_id: '',
      vote_status: '-1',
      status: undefined,
      upload_meta: {
        image_list:
          other_params_data && other_params_data.image_list ? other_params_data.image_list : [],
        document_list:
          other_params_data && other_params_data.document_list
            ? other_params_data.document_list
            : [],
        audio_list:
          other_params_data && other_params_data.audio_list ? other_params_data.audio_list : [],
        video_list:
          other_params_data && other_params_data.video_list ? other_params_data.video_list : [],
        other_list:
          other_params_data && other_params_data.other_list ? other_params_data.other_list : [],
      },
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
  if (chat.run_time) {
    ChatManagement.addChatRecord(chat, 50, loading)
    ChatManagement.write(chat.id)
  }
  if (!chartOpenId.value) {
    getChartOpenId(chat, problem, re_chat, other_params_data).catch(() => {
      errorWrite(chat)
    })
  } else {
    const obj = {
      message: chat.problem_text,
      stream: true,
      re_chat: re_chat || false,
      ...other_params_data,
      form_data: {
        ...form_data.value,
        ...api_form_data.value,
      },
    }
    // 对话
    getChatMessageAPI()(chartOpenId.value, obj)
      .then((response) => {
        if (response.status === 460) {
          return Promise.reject(t('chat.tip.errorIdentifyMessage'))
        } else if (response.status === 461) {
          return Promise.reject(t('chat.tip.errorLimitMessage'))
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
            response.headers.get('Content-Type') !== 'application/json',
          )
          return reader.read().then(write)
        }
      })
      .then(() => {
        if (props.chatId === 'new') {
          emit('refresh', chartOpenId.value)
        }
        getSourceDetail(chat)
        // if (props.type === 'debug-ai-chat') {
        //   getSourceDetail(chat)
        // } else {
        //   if (
        //     props.applicationDetails &&
        //     (props.applicationDetails.show_exec || props.applicationDetails.show_source)
        //   ) {
        //     getSourceDetail(chat)
        //   }
        // }
      })
      .finally(() => {
        ChatManagement.close(chat.id)
      })
      .catch((e: any) => {
        errorWrite(chat, e + '')
      })
  }
}

/**
 * 滚动条距离最上面的高度
 */
const scrollTop = ref(0)

const scorll = ref(true)
const isBottom = ref(false)

const getMaxHeight = () => {
  return dialogScrollbar.value!.scrollHeight
}

/**
 * 滚动滚动条到最上面
 * @param $event
 */
const handleScrollTop = ($event: any) => {
  scrollTop.value = $event.scrollTop
  if (
    dialogScrollbar.value.scrollHeight - (scrollTop.value + scrollDiv.value.wrapRef.offsetHeight) <=
    40
  ) {
    scorll.value = true
  } else {
    scorll.value = false
  }
  isBottom.value =
    scrollTop.value + scrollDiv.value.wrapRef.offsetHeight < dialogScrollbar.value!.scrollHeight
  emit('scroll', { ...$event, dialogScrollbar: dialogScrollbar.value, scrollDiv: scrollDiv.value })
}
/**
 * 处理跟随滚动条
 */
const handleScroll = () => {
  if (props.type !== 'log' && scrollDiv.value) {
    // 内部高度小于外部高度 就需要出滚动条
    if (scrollDiv.value.wrapRef.offsetHeight < dialogScrollbar.value.scrollHeight) {
      // 如果当前滚动条距离最下面的距离在 规定距离 滚动条就跟随
      if (scorll.value) {
        scrollDiv.value.setScrollTop(getMaxHeight())
      }
    }
  }
}
onBeforeMount(() => {
  window.chatUserProfile = () => {
    if (props.type === 'ai-chat') {
      if (chatUser.chat_profile?.authentication_type === 'login') {
        return chatUser.getChatUserProfile()
      }
    }
    return Promise.resolve(null)
  }
})
onMounted(() => {
  if (isUserInput.value && localStorage.getItem(`${accessToken}userForm`)) {
    const userFormData = JSON.parse(localStorage.getItem(`${accessToken}userForm`) || '{}')
    form_data.value = userFormData
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel()
  }

  window.sendMessage = sendMessage
  bus.on('on:transcribing', (status: boolean) => {
    transcribing.value = status
    nextTick(() => {
      if (scorll.value) {
        scrollDiv.value.setScrollTop(getMaxHeight())
      }
    })
  })
})

onBeforeUnmount(() => {
  window.sendMessage = null
  window.chatUserProfile = null
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
  { deep: true, immediate: true },
)

defineExpose({
  setScrollBottom,
})
</script>
<style lang="scss">
@use './index.scss';

.firstUserInput {
  height: 100%;
  display: flex;
  justify-content: center;
  overflow: auto;

  .user-form-container {
    max-width: 70%;
  }
}

.debug-ai-chat {
  .user-form-container {
    max-width: 100%;
  }
}

.popperUserInput {
  position: absolute;
  z-index: 999;
  left: 0;
  bottom: 50px;
  width: calc(100% - 50px);
  max-width: 400px;
}

.video-stop-button {
  box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);

  &:hover {
    background: #ffffff;
  }
}

@media only screen and (max-width: 768px) {
  .firstUserInput {
    .user-form-container {
      max-width: 100%;
    }
  }
}
</style>
