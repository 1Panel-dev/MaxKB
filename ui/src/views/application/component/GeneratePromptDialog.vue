<template>
  <el-dialog
    align-center
    :title="$t('views.application.generateDialog.generatePrompt')"
    v-model="dialogVisible"
    style="width: 600px"
    append-to-body
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    :before-close="handleDialogClose"
  >
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
              <el-icon class="is-loading color-primary mr-4"><Loading /></el-icon>
               {{ $t('views.application.generateDialog.loading') }}
              <span class="dotting"></span>
            </p>
            <p v-else class="flex align-center">
              <AppIcon iconName="app-generate-star" class="color-primary mr-4"></AppIcon>
              {{ $t('views.application.generateDialog.title') }}
            </p>
          </el-scrollbar>
          <div v-if="answer && !loading && !isStreaming && !showContinueButton">
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
              :placeholder="$t('views.application.generateDialog.placeholder')"
              :maxlength="100000"
              class="chat-operate-textarea"
              @keydown.enter="handleSubmit($event)"
            />

            <div class="operate">
              <div class="text-right">
                <el-button
                  text
                  class="sent-button"
                  :disabled="!inputValue.trim() || loading || isStreaming"
                  @click="handleSubmit"
                >
                  <img
                    v-show="!inputValue.trim() || loading || isStreaming"
                    src="@/assets/icon_send.svg"
                    alt=""
                  />
                  <SendIcon v-show="inputValue.trim() && !loading && !isStreaming" />
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onUnmounted, reactive, ref, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import systemGeneratePromptAPI from '@/api/system-resource-management/application'
import generatePromptAPI from '@/api/application/application'
import useStore from '@/stores'
const emit = defineEmits(['replace'])
const { user } = useStore()
const route = useRoute()

const chatMessages = ref<Array<any>>([])

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
// 原始输入
const originalUserInput = ref<string>('')
const modelID = ref('')
const applicationID = ref('')
const dialogVisible = ref(false)
const inputValue = ref<string>('')
const loading = ref<boolean>(false)

const promptTemplates = {
  INIT_TEMPLATE: `
请根据用户描述生成一个完整的AI角色人设模板:

用户需求：{userInput}

请按以下格式生成：

必须严格遵循以下规则：
1. **严格禁止输出解释、前言、额外说明**，只输出最终结果。
2. **严格使用以下格式**，不能缺少标题、不能多出其他段落。

# 角色:


## 目标：
角色的工作目标,如果有多目标可以分点列出,但建议更聚焦1-2个目标

## 技能：
1. 为了实现目标,角色需要具备的技能1
2. 为了实现目标,角色需要具备的技能2
3. 为了实现目标,角色需要具备的技能3

## 工作流：
1. 描述角色工作流程的第一步
2. 描述角色工作流程的第二步
3. 描述角色工作流程的第三步

## 输出格式：
如果对角色的输出格式有特定要求，可以在这里强调并举例说明想要的输出格式


## 限制：
1. **严格限制回答范围**：仅回答与角色设定相关的问题。
   - 如果用户提问与角色无关，必须使用以下固定格式回复：
     “对不起，我只能回答与【角色设定】相关的问题，您的问题不在服务范围内。”
   - 不得提供任何与角色设定无关的回答。
2. 描述角色在互动过程中需要遵循的限制条件2
3. 描述角色在互动过程中需要遵循的限制条件3

输出时不得包含任何解释或附加说明，只能返回符合以上格式的内容。
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
  }, 50) as  any
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
            if (!chunk.is_end) {
              // 实时将新接收的内容添加到完整内容中
              fullContent.value += chunk.content
              if (!streamingStarted) {
                streamingStarted = true
                startStreamingOutput()
              }
            }
            if (chunk.is_end) {
              isApiComplete.value = true
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
  loading.value = true
  const workspaceId = user.getWorkspaceId() || 'default'
  chatMessages.value.push({ content: inputValue, role: 'user' })
  const requestData = {
    messages: chatMessages.value,
    prompt: promptTemplates.INIT_TEMPLATE,
  }
  if (apiType.value === 'workspace') {
    generatePromptAPI
      .generate_prompt(workspaceId, modelID.value, applicationID.value, requestData)
      .then((response) => {
        nextTick(() => {
          if (dialogScrollbar.value) {
            // 将滚动条滚动到最下面
            scrollDiv.value.setScrollTop(getMaxHeight())
          }
        })
        const reader = response.body.getReader()
        reader.read().then(getWrite(reader))
      })
  } else if (apiType.value === 'systemManage') {
    console.log(apiType.value)
    systemGeneratePromptAPI
      .generate_prompt(applicationID.value, modelID.value, requestData)
      .then((response) => {
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
}

// 重新生成点击
const reAnswerClick = () => {
  if (originalUserInput.value) {
    generatePrompt('结果不满意,请按照格式,重新生成')
  }
}

const quickInputRef = ref()

const handleSubmit = (event?: any) => {
  if (!event?.ctrlKey && !event?.shiftKey && !event?.altKey && !event?.metaKey) {
    // 如果没有按下组合键，则会阻止默认事件
    event?.preventDefault()
    if (!originalUserInput.value) {
      originalUserInput.value = inputValue.value
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

const open = (modelId: string, applicationId: string) => {
  modelID.value = modelId
  applicationID.value = applicationId
  dialogVisible.value = true
  originalUserInput.value = ''
  chatMessages.value = []
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
    box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
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
    box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);

    &:hover {
      background: #ffffff;
    }
  }
}
</style>
