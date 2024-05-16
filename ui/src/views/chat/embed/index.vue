<template>
  <div class="chat" v-loading="loading">
    <div class="chat__header">
      <div class="chat-width">
        <h2 class="ml-24">{{ applicationDetail?.name }}</h2>
      </div>
    </div>
    <div class="chat__main chat-width">
      <AiChat
        v-model:data="applicationDetail"
        :available="applicationAvailable"
        :appId="applicationDetail?.id"
      ></AiChat>
    </div>
    <div class="chat__footer"></div>
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
  &__main {
    padding-top: calc(var(--app-header-height) + 24px);
    height: calc(100vh - var(--app-header-height) - 24px);
    overflow: hidden;
  }

  &__footer {
    background: #f3f7f9;
    height: 80px;
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
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
