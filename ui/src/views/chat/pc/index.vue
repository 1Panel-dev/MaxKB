<template>
  <div class="chat-pc" v-loading="loading">
    <div class="chat-pc__header">
      <h4 class="ml-24">{{ applicationDetail?.name }}</h4>
    </div>
    <div class="flex">
      <div class="chat-pc__left border-r">
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
                v-loading="left_loading"
                :defaultActive="currentChatId"
                @click="clickListHandle"
              >
                <template #default="{ row }">
                  <auto-tooltip :content="row.abstract">
                    {{ row.abstract }}
                  </auto-tooltip>
                </template>
                <template #empty>
                  <div class="text-center">
                    <el-text type="info">暂无历史记录</el-text>
                  </div>
                </template>
              </common-list>
            </div>
            <div v-if="chatLogeData.length" class="gradient-divider lighter mt-8">
              <span>仅显示最近 20 条对话</span>
            </div>
          </el-scrollbar>
        </div>
      </div>
      <div class="chat-pc__right">
        <div class="right-header border-b mb-24 p-16-24 flex-between">
          <h4>{{ currentChatName }}</h4>
          <span v-if="currentRecordList.length" class="flex align-center">
            <AppIcon iconName="app-chat-record" class="info mr-8" style="font-size: 16px"></AppIcon>
            <span class="lighter"> {{ paginationConfig.total }} 条提问 </span>
          </span>
        </div>
        <div class="right-height">
          <!-- 对话 -->
          <AiChat
            ref="AiChatRef"
            v-model:data="applicationDetail"
            :available="applicationAvailable"
            :appId="applicationDetail?.id"
            :record="currentRecordList"
            :chatId="currentChatId"
            @refresh="refresh"
            @scroll="handleScroll"
          ></AiChat>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import applicationApi from '@/api/application'
import useStore from '@/stores'
const route = useRoute()

const {
  params: { accessToken }
} = route as any

const { application, user, log } = useStore()

const newObj = {
  id: 'new',
  abstract: '新建对话'
}

const AiChatRef = ref()
const loading = ref(false)
const left_loading = ref(false)
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
const currentChatName = ref('新建对话')

function handleScroll(event: any) {
  if (
    currentChatId.value !== 'new' &&
    event.scrollTop === 0 &&
    paginationConfig.total > currentRecordList.value.length
  ) {
    const history_height = event.dialogScrollbar.offsetHeight
    paginationConfig.current_page += 1
    getChatRecord().then(() => {
      event.scrollDiv.setScrollTop(event.dialogScrollbar.offsetHeight - history_height)
    })
  }
}

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
    chatLogeData.value.unshift(newObj)
  } else {
    paginationConfig.current_page = 1
    currentRecordList.value = []
  }
  currentChatId.value = 'new'
  currentChatName.value = '新建对话'
}

function getChatLog(id: string) {
  const page = {
    current_page: 1,
    page_size: 20
  }

  log.asyncGetChatLogClient(id, page, left_loading).then((res: any) => {
    chatLogeData.value = res.data.records
  })
}

function getChatRecord() {
  return log
    .asyncChatRecordLog(
      applicationDetail.value.id,
      currentChatId.value,
      paginationConfig,
      loading,
      false
    )
    .then((res: any) => {
      paginationConfig.total = res.data.total
      const list = res.data.records
      list.map((v: any) => {
        v['write_ed'] = true
      })
      currentRecordList.value = [...list, ...currentRecordList.value].sort((a, b) =>
        a.create_time.localeCompare(b.create_time)
      )
      if (paginationConfig.current_page === 1) {
        nextTick(() => {
          // 将滚动条滚动到最下面
          AiChatRef.value.setScrollBottom()
        })
      }
    })
}
const clickListHandle = (item: any) => {
  if (item.id !== currentChatId.value) {
    paginationConfig.current_page = 1
    currentRecordList.value = []
    currentChatId.value = item.id
    currentChatName.value = item.abstract
    if (currentChatId.value !== 'new') {
      getChatRecord()
    }
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
    padding-top: calc(var(--app-header-height));
    overflow: hidden;
    position: relative;
    .right-header {
      background: #ffffff;
    }
    .right-height {
      height: calc(100vh - var(--app-header-height) * 2 - 24px);
      overflow: scroll;
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
