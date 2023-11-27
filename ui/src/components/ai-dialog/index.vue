<template>
  <div class="ai-dialog p-24">
    <el-scrollbar>
      <div class="ai-dialog__content">
        <div class="item-content mb-16">
          <div class="avatar">
            <AppAvatar class="avatar-gradient">
              <img src="@/assets/icon_robot.svg" style="width: 54%" alt="" />
            </AppAvatar>
            <!-- <AppAvatar>
            <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
          </AppAvatar> -->
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
        <div class="item-content mb-16">
          <div class="avatar">
            <AppAvatar>
              <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
            </AppAvatar>
          </div>
          <div class="content">
            <div class="text">
              XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            </div>
          </div>
        </div>
        <div class="item-content mb-16">
          <div class="avatar">
            <AppAvatar class="avatar-gradient">
              <img src="@/assets/icon_robot.svg" style="width: 54%" alt="" />
            </AppAvatar>
          </div>
          <div class="content">
            <el-card shadow="always" class="dialog-card"> XXXXXXXXX </el-card>
          </div>
        </div>
      </div>
    </el-scrollbar>
    <div class="ai-dialog__operate p-24">
      <div class="operate-textarea flex">
        <el-input
          v-model="inputValue"
          type="textarea"
          placeholder="请输入"
          :autosize="{ minRows: 1, maxRows: 8 }"
        />
        <div class="operate" v-loading="loading">
          <el-button
            text
            class="sent-button"
            :disabled="!(inputValue && data?.name && data?.model_id)"
            @click="chatMessage"
          >
            <img
              v-show="!(inputValue && data?.name && data?.model_id)"
              src="@/assets/icon_send.svg"
              alt=""
            />
            <img
              v-show="inputValue && data?.name && data?.model_id"
              src="@/assets/icon_send_colorful.svg"
              alt=""
            />
            <!-- <AppIcon iconName="app-send"></AppIcon> -->
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import applicationApi from '@/api/application'
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})
const loading = ref(false)
const inputValue = ref('')
const chartOpenId = ref('')

function quickProblemHandel(val: string) {
  inputValue.value = val
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

function chatMessage() {
  if (!chartOpenId.value) {
    getChartOpenId()
  } else {
    applicationApi.postChatMessage(chartOpenId.value, inputValue.value).then(async (response) => {
      const reader = response.body.getReader()
      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          loading.value = false
          break
        }
        const decoder = new TextDecoder('utf-8')
        const str = decoder.decode(value, { stream: true })
        console.log('value', JSON.parse(str.replace('data:', '')))
      }
    })
  }
}
</script>
<style lang="scss" scoped>
.ai-dialog {
  --padding-left: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  padding-right: 20px;
  padding-top: 0;
  &__content {
    width: 99%;
    padding-bottom: 96px;
    .avatar {
      float: left;
    }
    .content {
      padding-left: var(--padding-left);
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
    padding-top: 16px;
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
