<template>
  <div class="chat-pc" v-loading="loading">
    <div class="chat-pc__header">
      <h4 class="ml-24">{{ applicationDetail?.name }}</h4>
    </div>
    <div class="flex">
      <div class="chat-pc__left">
        <div class="p-24 pb-0">
          <el-button class="add-button w-full primary" @click="newChat">
            <el-icon><Plus /></el-icon><span class="ml-4">新建对话</span>
          </el-button>
          <p class="mt-20 mb-8">历史记录</p>
        </div>
        <div class="left-height pt-0">
          <el-scrollbar>
            <div class="p-8 pt-0">
              <common-list
                :data="chatLogeData"
                class="mt-8"
                v-loading="loading"
                :defaultActive="currentChatId"
                @click="clickListHandle"
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
      <div class="chat-pc__right">
        <div class="right-height">
          <AiChat
            v-model:data="applicationDetail"
            :available="applicationAvailable"
            :appId="applicationDetail?.id"
            :record="currentRecordList"
            :chatId="currentChatId"
            @refresh="refresh"
          ></AiChat>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
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

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

const currentRecordList = ref<any>([])
const currentChatId = ref('new') // 当前历史记录Id 默认为'new'

function getAccessToken(token: string) {
  application
    .asyncAppAuthentication(token, loading)
    .then(() => {
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

function newChat() {
  if (!chatLogeData.value.some((v) => v.id === 'new')) {
    paginationConfig.current_page = 1
    currentRecordList.value = []

    chatLogeData.value.unshift({
      id: 'new',
      abstract: '新的对话'
    })
  } else {
    paginationConfig.current_page = 1
    currentRecordList.value = []
  }
  currentChatId.value = 'new'
}

function getChatLog(id: string) {
  const page = {
    current_page: 1,
    page_size: 20
  }

  log.asyncGetChatLogClient(id, page, loading).then((res: any) => {
    chatLogeData.value = res.data.records
  })
}

function getChatRecord() {
  log
    .asyncChatRecordLog(applicationDetail.value.id, currentChatId.value, paginationConfig, loading)
    .then((res: any) => {
      paginationConfig.total = res.data.total
      const list = res.data.records
      list.map((v: any) => {
        v['write_ed'] = true
      })
      currentRecordList.value = [...currentRecordList.value, ...list]
    })
}
const clickListHandle = (item: any) => {
  paginationConfig.current_page = 1
  currentRecordList.value = []
  currentChatId.value = item.id
  if (currentChatId.value !== 'new') {
    getChatRecord()
  }
}

function refresh(id: string) {
  getChatLog(applicationDetail.value.id)
  currentChatId.value = id
}

onMounted(() => {
  user.changeUserType(2)
  getAccessToken(accessToken)
})
</script>
<style lang="scss">
.chat-pc {
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
    .left-height {
      height: calc(100vh - var(--app-header-height) - 135px);
    }
  }
  &__right {
    width: calc(100% - 280px);
    padding-top: calc(var(--app-header-height) + 24px);

    overflow: hidden;
    position: relative;
    .right-height {
      height: calc(100vh - var(--app-header-height) - 24px);
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
