<template>
  <div class="chat" v-loading="loading">
    <div class="chat__header">
      <h4 class="ml-24">{{ applicationDetail?.name }}</h4>
    </div>
    <div class="flex">
      <div class="chat__left">
        <div class="p-24 pb-0">
          <el-button class="add-button w-full primary">
            <el-icon><Plus /></el-icon><span class="ml-4">新建对话</span>
          </el-button>
          <p class="mt-20 mb-8">历史记录</p>
        </div>
        <div class="chat-list-height pt-0">
          <el-scrollbar>
            <div class="p-8 pt-0">
              <common-list
                :data="chatLogeData"
                class="mt-8"
                v-loading="loading"
                @click="clickMemberHandle"
              >
                <template #default="{ row }">
                  <auto-tooltip :content="row.abstract">
                    {{ row.abstract }}
                  </auto-tooltip>
                </template>
              </common-list>
            </div>
            <div class="gradient-divider lighter mt-8"><span>仅显示最近 20 条对话</span></div>
          </el-scrollbar>
        </div>
      </div>
      <div class="chat__right w-full">
        <AiChat
          v-model:data="applicationDetail"
          :available="applicationAvailable"
          :appId="applicationDetail?.id"
        ></AiChat>
      </div>
      <div class="chat__footer"></div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import applicationApi from '@/api/application'
import useStore from '@/stores'
const route = useRoute()
const {
  params: { accessToken }
} = route as any

const { application, user, log } = useStore()

const loading = ref(false)
const applicationDetail = ref<any>({})
const applicationAvailable = ref<boolean>(true)
const chatLogeData = ref<any[]>([])

function getAccessToken(token: string) {
  application
    .asyncAppAuthentication(token, loading)
    .then((res) => {
      getProfile()
    })
    .catch(() => {
      applicationAvailable.value = false
    })
}
function getProfile() {
  applicationApi
    .getProfile(loading)
    .then((res) => {
      applicationDetail.value = res.data
      getChatLog(applicationDetail.value.id)
    })
    .catch(() => {
      applicationAvailable.value = false
    })
}

function getChatLog(id: string) {
  const page = {
    current_page: 1,
    page_size: 20
  }
  const param = {
    history_day: 183
  }

  log.asyncGetChatLog(id, page, param, loading).then((res: any) => {
    chatLogeData.value = res.data.records
  })
}

onMounted(() => {
  user.changeUserType(2)
  getAccessToken(accessToken)
})
</script>
<style lang="scss">
.chat {
  background-color: var(--app-layout-bg-color);
  overflow: hidden;
  &__header {
    background: var(--app-header-bg-color);
    position: fixed;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 100;
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-border-color);
  }
  &__left {
    padding-top: calc(var(--app-header-height) - 8px);

    background: #ffffff;
    width: 280px;
    .add-button {
      border: 1px solid var(--el-color-primary);
    }
    .chat-list-height {
      height: calc(100vh - var(--app-header-height) - 160px);
    }
  }
  &__right {
    width: calc(100% - 280px);
    padding-top: calc(var(--app-header-height) + 24px);
    height: calc(100vh - var(--app-header-height) - 30px);
    overflow: hidden;
    position: relative;
  }

  &__footer {
    background: #f3f7f9;
    height: 80px;
    position: absolute;
    bottom: 0;
    left: 280px;
    width: calc(100% - 280px);
    box-sizing: border-box;
    border-radius: 8px !important;
    &:before {
      background: linear-gradient(0deg, #f3f7f9 0%, rgba(243, 247, 249, 0) 100%);
      content: '';
      position: absolute;
      width: 100%;
      top: -16px;
      left: 0;
      height: 16px;
    }
  }
  .gradient-divider {
    position: relative;
    text-align: center;
    color: var(--el-color-info);
    ::before {
      content: '';
      width: 17%;
      height: 1px;
      background: linear-gradient(90deg, rgba(222, 224, 227, 0) 0%, #dee0e3 100%);
      position: absolute;
      left: 16px;
      top: 50%;
    }
    ::after {
      content: '';
      width: 17%;
      height: 1px;
      background: linear-gradient(90deg, #dee0e3 0%, rgba(222, 224, 227, 0) 100%);
      position: absolute;
      right: 16px;
      top: 50%;
    }
  }
  .chat-width {
    max-width: var(--app-chat-width, 860px);
    margin: 0 auto;
  }
}
</style>
