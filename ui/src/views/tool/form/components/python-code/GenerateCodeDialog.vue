<template>
  <el-dialog
    align-center
    v-model="dialogVisible"
    style="width: 800px"
    append-to-body
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    :before-close="handleDialogClose"
  >
    <template #title>
      <div class="flex-between">
        <h4>{{ $t('views.tool.generateCodeDialog.generatePrompt') }}</h4>
        <div class="flex align-center">
          <div class="mr-4 lighter">{{ $t('views.application.form.aiModel.label') }}</div>
          <ModelSelect
            v-model="model_id"
            :placeholder="$t('views.application.form.aiModel.placeholder')"
            :options="modelOptions"
            @change="model_change"
            @submitModel="getSelectModel"
            showFooter
            :model-type="'LLM'"
            style="width: 200px"
          >
          </ModelSelect>
          <el-button class="ml-8" @click="openAIParamSettingDialog" :disabled="!model_id">
            <el-icon>
              <Operation />
            </el-icon>
          </el-button>
        </div>
      </div>
    </template>
    <div class="generate-prompt-dialog-bg border-r-8">
      <div class="scrollbar-height">
        <!-- 生成内容 -->
        <div class="p-16 pb-0 lighter">
          <el-scrollbar ref="scrollDiv">
            <div
              ref="dialogScrollbar"
              v-if="answer"
              class="pre-wrap lighter"
              style="max-height: calc(100vh - 400px)"
            >
              {{ answer }}
            </div>
            <p v-else-if="loading" shadow="always" style="margin: 0.5rem 0">
              <el-icon class="is-loading color-primary mr-4">
                <Loading />
              </el-icon>
              {{ $t('views.application.generateDialog.loading') }}
              <span class="dotting"></span>
            </p>
            <p v-else class="flex align-center">
              <AppIcon iconName="app-generate-star" class="color-primary mr-4"></AppIcon>
              {{ $t('views.tool.generateCodeDialog.title') }}
            </p>
          </el-scrollbar>

          <div v-if="answer && !loading && !isStreaming && !showContinueButton" class="mt-8">
            <el-button type="primary" @click="() => emit('replace', answer)">
              {{ $t('views.application.generateDialog.replace') }}
            </el-button>
            <el-button @click="reAnswerClick" :disabled="!answer || loading" :loading="loading">
              {{ $t('views.application.generateDialog.remake') }}
            </el-button>
          </div>
          <div class="mt-8" v-else>
            <el-button type="primary" v-if="showContinueButton" @click="continueStreaming" link>
              {{ $t('views.application.generateDialog.continue') }}
            </el-button>
          </div>
        </div>

        <!-- 文本输入框 -->

        <div class="generate-prompt-operate p-16">
          <div v-if="showStopButton" class="text-center mb-8">
            <el-button class="border-primary video-stop-button" @click="pauseStreaming">
              <app-icon iconName="app-video-stop" class="mr-8"></app-icon>
              {{ $t('views.application.generateDialog.stop') }}
            </el-button>
          </div>

          <div class="operate-textarea">
            <el-input
              ref="quickInputRef"
              v-model="inputValue"
              :autosize="{ minRows: 1, maxRows: 10 }"
              type="textarea"
              :placeholder="$t('views.tool.generateCodeDialog.placeholder')"
              :maxlength="100000"
              class="chat-operate-textarea"
              @keydown.enter="handleSubmit($event)"
            />

            <div class="operate">
              <div class="text-right">
                <el-button
                  text
                  class="sent-button"
                  :disabled="!inputValue.trim() || loading || isStreaming || !model_id"
                  @click="handleSubmit"
                >
                  <img
                    v-show="!inputValue.trim() || loading || isStreaming || !model_id"
                    src="@/assets/chat/icon_send.svg"
                    alt=""
                  />
                  <SendIcon v-show="inputValue.trim() && !loading && !isStreaming && model_id" />
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshForm" />
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
import { copyClick } from '@/utils/clipboard'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { groupBy } from 'lodash'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import SendIcon from '@/components/logo/SendIcon.vue'

const emit = defineEmits(['replace'])
const { user } = useStore()
const route = useRoute()

const chatMessages = ref<Array<any>>([])

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
// 原始输入
const originalUserInput = ref<string>('')
const dialogVisible = ref(false)
const inputValue = ref<string>('')
const loading = ref<boolean>(false)
const modelOptions = ref<any>(null)
const inputFieldList = ref<Array<any>>([])
const initFieldList = ref<Array<any>>([])
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()
const model_id = ref('')
const model_params_setting = ref({})

const promptTemplates = {
  INIT_TEMPLATE: `你是资深的 Python 工程师，专注于为 MaxKB 平台的工具 / 数据源场景生成可直接运行的 Python 代码。严格遵守以下规则：

- 仅输出纯 Python 代码块，无任何多余的文字解释、注释以外的说明；
- 代码兼容 Python 3.8 及以上版本，符合 PEP8 编码规范，关键逻辑添加简洁中文注释；
- 仅使用 MaxKB 内置依赖（如 requests、pymysql、pandas、json 等），不引入未声明的第三方库。

{userInput}

请为 MaxKB 工具 生成 Python 代码，需求如下：

- 核心功能：用户输入的主题 / 功能需求
- 启动参数：平台配置的启动参数，如 API 密钥、数据库地址、账号密码等, 已声明参数：{initFieldList}
- 输入参数：平台配置的输入参数，已声明参数：{inputFieldList}
- 函数定义：依次列举所有启动参数和输入参数并声明返回类型
- 输出要求：代码需接收输入参数，启动参数完成业务逻辑，仅输出函数定义
`,
}

const isStreaming = ref<boolean>(false) // 是否正在流式输出
const isPaused = ref<boolean>(false) // 是否暂停
const fullContent = ref<string>('') // 完整内容缓存
const currentDisplayIndex = ref<number>(0) // 当前显示到的字符位置
let streamTimer: number | null = null // 定时器引用
const isOutputComplete = ref<boolean>(false)

// 模拟流式输出的定时器函数
const startStreamingOutput = () => {
  if (streamTimer) {
    clearInterval(streamTimer)
  }

  isStreaming.value = true
  isPaused.value = false

  streamTimer = setInterval(() => {
    if (isApiComplete.value && !isPaused.value) {
      // 更新显示内容
      const currentAnswer = chatMessages.value[chatMessages.value.length - 1]
      if (currentAnswer && currentAnswer.role === 'ai') {
        currentAnswer.content = fullContent.value
      }
      stopStreaming()
      return
    }
    if (!isPaused.value && currentDisplayIndex.value < fullContent.value.length) {
      // 每次输出1-3个字符，模拟真实的流式输出
      const step = Math.min(3, fullContent.value.length - currentDisplayIndex.value)
      currentDisplayIndex.value += step

      // 更新显示内容
      const currentAnswer = chatMessages.value[chatMessages.value.length - 1]
      if (currentAnswer && currentAnswer.role === 'ai') {
        currentAnswer.content = fullContent.value.substring(0, currentDisplayIndex.value)
      }
    } else if (loading.value === false && currentDisplayIndex.value >= fullContent.value.length) {
      stopStreaming()
    }
  }, 50) as any
}

// 停止流式输出
const stopStreaming = () => {
  if (streamTimer) {
    clearInterval(streamTimer)
    streamTimer = null
  }
  isStreaming.value = false
  isPaused.value = false
  loading.value = false
  isOutputComplete.value = true
}

const showStopButton = computed(() => {
  return isStreaming.value
})

// 暂停流式输出
const pauseStreaming = () => {
  isPaused.value = true
  isStreaming.value = false
}

// 继续流式输出
const continueStreaming = () => {
  if (currentDisplayIndex.value < fullContent.value.length) {
    startStreamingOutput()
  }
}

/**
 * 获取一个递归函数,处理流式数据
 * @param chat    每一条对话记录
 * @param reader  流数据
 * @param stream  是否是流式数据
 */
const getWrite = (reader: any) => {
  let tempResult = ''
  const middleAnswer = reactive({ content: '', role: 'ai' })
  chatMessages.value.push(middleAnswer)

  // 初始化状态并
  fullContent.value = ''
  currentDisplayIndex.value = 0
  isOutputComplete.value = false

  let streamingStarted = false

  /**
   *
   * @param done  是否结束
   * @param value 值
   */
  const write_stream = ({ done, value }: { done: boolean; value: any }) => {
    try {
      if (done) {
        // 流数据接收完成，但定时器继续运行直到显示完所有内容
        loading.value = false
        isApiComplete.value = true
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
            if (chunk.error) {
              loading.value = false
              stopStreaming()
              middleAnswer.content = chunk.error
              return Promise.reject(new Error(chunk.error))
            }
            if (!chunk.is_end) {
              // 实时将新接收的内容添加到完整内容中
              fullContent.value += chunk.content
              if (!streamingStarted) {
                streamingStarted = true
                startStreamingOutput()
              }
            }
            if (chunk.is_end) {
              return Promise.resolve()
            }
          }
        }
      }
    } catch (e) {
      loading.value = false
      stopStreaming()
      return Promise.reject(e)
    }
    return reader.read().then(write_stream)
  }

  return write_stream
}
const isApiComplete = ref<boolean>(false)
const answer = computed(() => {
  const result = chatMessages.value[chatMessages.value.length - 1]

  if (result && result.role == 'ai') {
    return result.content
  }
  return ''
})

// 按钮状态计算
const showContinueButton = computed(() => {
  return (
    !isStreaming.value && isPaused.value && currentDisplayIndex.value < fullContent.value.length
  )
})

function generatePrompt(inputValue: any) {
  isApiComplete.value = false
  loading.value = true
  const workspaceId = user.getWorkspaceId() || 'default'
  chatMessages.value.push({ content: inputValue, role: 'user' })
  const requestData = {
    messages: chatMessages.value,
    prompt: promptTemplates.INIT_TEMPLATE,
    init_field_list: initFieldList.value,
    input_field_list: inputFieldList.value,
    model_id: model_id.value,
    model_params_setting: model_params_setting.value,
  }

  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .generateCode(requestData)
    .then((response: any) => {
      nextTick(() => {
        if (dialogScrollbar.value) {
          // 将滚动条滚动到最下面
          scrollDiv.value.setScrollTop(getMaxHeight())
        }
      })
      const reader = response.body.getReader()
      reader.read().then(getWrite(reader))
    })
}

// 重新生成点击
const reAnswerClick = () => {
  if (originalUserInput.value) {
    generatePrompt(
      `上一次回答不满意。请针对原始问题"${originalUserInput.value}"并结合对话记录，严格按照格式规范重新生成。`,
    )
  }
}

const quickInputRef = ref()

const handleSubmit = (event?: any) => {
  if (!event?.ctrlKey && !event?.shiftKey && !event?.altKey && !event?.metaKey) {
    // 如果没有按下组合键，则会阻止默认事件
    event?.preventDefault()
    if (!inputValue.value.trim() || loading.value || isStreaming.value || !model_id.value) {
      return
    }
    if (!originalUserInput.value) {
      originalUserInput.value = inputValue.value
    }
    if (isPaused.value || isStreaming.value) {
      return
    }
    if (inputValue.value) {
      generatePrompt(inputValue.value)
      inputValue.value = ''
    }
  } else {
    // 如果同时按下ctrl/shift/cmd/opt +enter，则会换行
    insertNewlineAtCursor(event)
  }
}
const insertNewlineAtCursor = (event?: any) => {
  const textarea = quickInputRef.value.$el.querySelector(
    '.el-textarea__inner',
  ) as HTMLTextAreaElement
  const startPos = textarea.selectionStart
  const endPos = textarea.selectionEnd
  // 阻止默认行为（避免额外的换行符）
  event.preventDefault()
  // 在光标处插入换行符
  inputValue.value = inputValue.value.slice(0, startPos) + '\n' + inputValue.value.slice(endPos)
  nextTick(() => {
    textarea.setSelectionRange(startPos + 1, startPos + 1) // 光标定位到换行后位置
  })
}

function getSelectModel() {
  loading.value = true

  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'LLM',
          // todo workspace_id
          workspace_id: '',
        }
      : {
          model_type: 'LLM',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

const model_change = (modelId: string) => {
  model_id.value = modelId
  if (modelId) {
    AIModeParamSettingDialogRef.value?.reset_default(modelId)
  } else {
    refreshForm({})
  }
}

const openAIParamSettingDialog = () => {
  if (model_id.value) {
    AIModeParamSettingDialogRef.value?.open(model_id.value, '', model_params_setting.value)
  }
}

function refreshForm(data: any) {
  model_params_setting.value = data
}

const open = (init_field_list: any, input_field_list: any) => {
  dialogVisible.value = true
  originalUserInput.value = ''
  chatMessages.value = []
  initFieldList.value = init_field_list || []
  inputFieldList.value = input_field_list || []
}

const scrollDiv = ref()
const dialogScrollbar = ref()

const getMaxHeight = () => {
  return dialogScrollbar.value!.scrollHeight
}

/**
 * 处理跟随滚动条
 */
const handleScroll = () => {
  if (scrollDiv.value) {
    // 内部高度小于外部高度 就需要出滚动条
    if (scrollDiv.value.wrapRef.offsetHeight < dialogScrollbar.value?.scrollHeight) {
      // 如果当前滚动条距离最下面的距离在 规定距离 滚动条就跟随
      scrollDiv.value.setScrollTop(getMaxHeight())
    }
  }
}

const handleDialogClose = (done: () => void) => {
  if (answer.value) {
    // 弹出 消息
    MsgConfirm(t('common.tip'), t('views.application.generateDialog.exit'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      distinguishCancelAndClose: true,
    })
      .then(() => {
        // 点击确认，清除状态
        stopStreaming()
        chatMessages.value = []
        fullContent.value = ''
        currentDisplayIndex.value = 0
        isOutputComplete.value = false
        done() // 真正关闭
      })
      .catch(() => {
        // 点击取消
      })
  } else {
    done()
  }
}

// 组件卸载时清理定时器
onUnmounted(() => {
  stopStreaming()
})

watch(
  answer,
  () => {
    handleScroll()
  },
  { deep: true, immediate: true },
)

onMounted(() => {
  getSelectModel()
})

defineExpose({
  open,
})
</script>

<style lang="scss" scoped>
.generate-prompt-dialog-bg {
  background: var(--dialog-bg-gradient-color);
  overflow: hidden;
  box-sizing: border-box;
}

.generate-prompt-operate {
  position: relative;
  width: 100%;
  box-sizing: border-box;
  z-index: 10;

  :deep(.operate-textarea) {
    box-shadow: 0px 6px 24px 0px rgba(var(--el-text-color-primary-rgb), 0.08);
    background-color: #ffffff;
    border-radius: var(--app-border-radius-large);
    border: 1px solid #ffffff;
    box-sizing: border-box;

    &:has(.el-textarea__inner:focus) {
      border: 1px solid var(--el-color-primary);
    }

    .el-textarea__inner {
      border-radius: var(--app-border-radius-large) !important;
      box-shadow: none;
      resize: none;
      padding: 13px 16px;
      box-sizing: border-box;
      min-height: 47px !important;
      height: 0;
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

      .el-loading-spinner {
        margin-top: -15px;

        .circular {
          width: 31px;
          height: 31px;
        }
      }
    }
  }

  .video-stop-button {
    box-shadow: 0px 6px 24px 0px rgba(var(--el-text-color-primary-rgb), 0.08);

    &:hover {
      background: #ffffff;
    }
  }
}
</style>
