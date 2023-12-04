<template>
  <div class="ai-dialog">
    <el-scrollbar ref="scrollDiv">
      <div ref="dialogScrollbar" class="ai-dialog__content p-24">
        <div class="item-content mb-16">
          <div class="avatar">
            <AppAvatar class="avatar-gradient">
              <img src="@/assets/icon_robot.svg" style="width: 54%" alt="" />
            </AppAvatar>
          </div>

          <div class="content">
            <el-card shadow="always" class="dialog-card">
              <h4>您好，我是 MaxKB 智能小助手</h4>
              <div class="mt-4" v-if="data?.prologue">
                <el-text type="info">{{ data?.prologue }}</el-text>
              </div>
            </el-card>
            <el-card shadow="always" class="dialog-card mt-12" v-if="data?.example?.length > 0">
              <h4 class="mb-8">您可以尝试输入以下问题：</h4>
              <el-space wrap>
                <template v-for="(item, index) in data?.example" :key="index">
                  <div
                    @click="quickProblemHandel(item)"
                    class="problem-button cursor ellipsis-2"
                    v-if="item"
                  >
                    <el-icon><EditPen /></el-icon>
                    {{ item }}
                  </div>
                </template>
              </el-space>
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
              <div class="text">
                {{ item.problem_text }}
              </div>
            </div>
          </div>
          <!-- 回答 -->
          <div class="item-content mb-16 lighter">
            <div class="avatar">
              <AppAvatar class="avatar-gradient">
                <img src="@/assets/icon_robot.svg" style="width: 54%" alt="" />
              </AppAvatar>
            </div>
            <div class="content">
              <div class="flex" v-if="!item.answer_text">
                <el-card shadow="always" class="dialog-card">
                  回答中 <span class="dotting"></span>
                </el-card>
              </div>
              <el-card v-else shadow="always" class="dialog-card">
                <MarkdownRenderer
                  :source="item.answer_text"
                  :inner_suffix="false"
                ></MarkdownRenderer>
              </el-card>
              <div class="flex-between mt-8">
                <div>
                  <el-button
                    type="primary"
                    v-if="item.is_stop && !item.write_ed"
                    @click="startChat(item)"
                    link
                    >继续</el-button
                  >
                  <el-button type="primary" v-else-if="!item.write_ed" @click="stopChat(item)" link
                    >停止回答</el-button
                  >
                </div>

                <div v-if="item.write_ed && props.appId">
                  <OperationButton
                    :data="item"
                    :applicationId="appId"
                    :chartId="chartOpenId"
                    @regeneration="regenerationChart(item)"
                  />
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </el-scrollbar>
    <div class="ai-dialog__operate p-24">
      <div class="operate-textarea flex">
        <el-input
          v-model="inputValue"
          type="textarea"
          placeholder="请输入"
          :autosize="{ minRows: 1, maxRows: 8 }"
          @keydown.enter="sendChatHandle($event)"
          :disabled="loading"
        />
        <div class="operate" v-loading="loading">
          <el-button text class="sent-button" :disabled="isDisabledChart" @click="sendChatHandle">
            <img v-show="isDisabledChart" src="@/assets/icon_send.svg" alt="" />
            <img v-show="!isDisabledChart" src="@/assets/icon_send_colorful.svg" alt="" />
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, onUpdated, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import OperationButton from './OperationButton.vue'
import applicationApi from '@/api/application'
import { ChatManagement, type chatType } from '@/api/type/application'
import { randomId } from '@/utils/utils'
import useStore from '@/stores'
const route = useRoute()
const {
  params: { accessToken }
} = route as any
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  appId: String
})
const { application } = useStore()

const scrollDiv = ref()
const dialogScrollbar = ref()
const loading = ref(false)
const inputValue = ref('')
const problem_text = ref('') //备份问题
const chartOpenId = ref('')
const chatList = ref<chatType[]>([])

const isDisabledChart = computed(
  () => !(inputValue.value && (props.appId || (props.data?.name && props.data?.model_id)))
)

function quickProblemHandel(val: string) {
  inputValue.value = val
}

function sendChatHandle(event: any) {
  if (!event.ctrlKey) {
    // 如果没有按下组合键ctrl，则会阻止默认事件
    event.preventDefault()
    if (!isDisabledChart.value) {
      chatMessage()
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
function getChartOpenId() {
  loading.value = true
  const obj = {
    model_id: props.data.model_id,
    dataset_id_list: props.data.dataset_id_list,
    multiple_rounds_dialogue: props.data.multiple_rounds_dialogue
  }
  if (props.appId) {
    applicationApi
      .getChatOpen(props.appId)
      .then((res) => {
        chartOpenId.value = res.data
        chatMessage()
      })
      .catch((res) => {
        if (res.response.status === 403) {
          application.asyncAppAuthentication(accessToken).then(() => {
            getChartOpenId()
          })
        }
        loading.value = false
      })
  } else {
    applicationApi
      .postChatOpen(obj)
      .then((res) => {
        chartOpenId.value = res.data
        chatMessage()
      })
      .catch(() => {
        loading.value = false
      })
  }
}

function chatMessage() {
  loading.value = true
  if (!chartOpenId.value) {
    getChartOpenId()
  } else {
    const problem_text = inputValue.value
    const id = randomId()
    chatList.value.push({
      id: id,
      problem_text: problem_text,
      answer_text: '',
      buffer: [],
      write_ed: false,
      is_stop: false,
      record_id: '',
      vote_status: '-1'
    })
    applicationApi.postChatMessage(chartOpenId.value, problem_text).then(async (response) => {
      inputValue.value = ''
      const row = chatList.value.find((item) => item.id === id)

      if (row) {
        ChatManagement.addChatRecord(row, 50, loading)
        ChatManagement.write(id)
        const reader = response.body.getReader()
        /*eslint no-constant-condition: ["error", { "checkLoops": false }]*/
        while (true) {
          const { done, value } = await reader.read()
          if (done) {
            ChatManagement.close(id)
            break
          }
          try {
            const decoder = new TextDecoder('utf-8')
            const str = decoder.decode(value, { stream: true })

            if (str && str.startsWith('data:')) {
              row.record_id = JSON?.parse(str.replace('data:', '')).id
              const content = JSON?.parse(str.replace('data:', ''))?.content
              if (content) {
                ChatManagement.append(id, content)
              }
            }
          } catch (e) {
            //  console
          }
        }
      }
    })
  }
}

function regenerationChart(item: chatType) {
  inputValue.value = item.problem_text
  chatMessage()
}

// 滚动到底部
function handleScrollBottom() {
  nextTick(() => {
    scrollDiv.value.setScrollTop(dialogScrollbar.value.scrollHeight)
  })
}

onUpdated(() => {
  handleScrollBottom()
})
</script>
<style lang="scss" scoped>
.ai-dialog {
  --padding-left: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  color: var(--app-text-color);
  &__content {
    padding-top: 0;
    padding-bottom: 96px;
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
      word-break: break-all;
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
      :deep(.el-icon) {
        color: var(--el-color-primary);
      }
    }
  }
  &__operate {
    background: #f3f7f9;
    position: absolute;
    bottom: 0;
    left: 0;
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
      }
      .operate {
        padding: 6px 10px;
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
  }
}
</style>
