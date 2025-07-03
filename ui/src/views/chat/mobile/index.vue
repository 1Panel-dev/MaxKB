<template>
  <div
    class="chat-mobile layout-bg chat-background"
    v-loading="loading"
    :style="{
      '--el-color-primary': applicationDetail?.custom_theme?.theme_color,
      '--el-color-primary-light-9': hexToRgba(applicationDetail?.custom_theme?.theme_color, 0.1),
      backgroundImage: `url(${applicationDetail?.chat_background})`,
    }"
  >
    <div class="chat-embed__header" :style="(user.isEE() || user.isPE()) && customStyle">
      <div class="flex align-center">
        <AppIcon
          iconName="app-history-outlined"
          style="font-size: 20px"
          class="ml-16"
          :style="{
            color: applicationDetail?.custom_theme?.header_font_color,
          }"
          @click.prevent.stop="show = true"
        />
        <div class="mr-12 ml-16 flex">
          <el-avatar
            v-if="isAppIcon(applicationDetail?.icon)"
            shape="square"
            :size="32"
            style="background: none"
          >
            <img :src="applicationDetail?.icon" alt="" />
          </el-avatar>
          <LogoIcon v-else height="32px" />
        </div>

        <h4>{{ applicationDetail?.name }}</h4>
      </div>
    </div>
    <div>
      <div class="chat-embed__main">
        <AiChat
          ref="AiChatRef"
          v-model:applicationDetails="applicationDetail"
          :available="applicationAvailable"
          :appId="applicationDetail?.id"
          :record="currentRecordList"
          :chatId="currentChatId"
          type="ai-chat"
          @refresh="refresh"
          @scroll="handleScroll"
          class="AiChat-embed"
        >
          <template #operateBefore>
            <div>
              <el-button type="primary" link class="new-chat-button mb-8" @click="newChat">
                <el-icon><Plus /></el-icon><span class="ml-4">{{ $t('chat.createChat') }}</span>
              </el-button>
            </div>
          </template>
        </AiChat>
      </div>

      <el-drawer
        v-model="show"
        :with-header="false"
        class="left-drawer"
        direction="ltr"
        :size="280"
      >
        <div>
          <div class="flex align-center mb-16">
            <div class="flex mr-8">
              <el-avatar
                v-if="isAppIcon(applicationDetail?.icon)"
                shape="square"
                :size="32"
                style="background: none"
              >
                <img :src="applicationDetail?.icon" alt="" />
              </el-avatar>
              <LogoIcon v-else height="32px" />
            </div>
            <h4>{{ applicationDetail?.name }}</h4>
          </div>
          <el-button class="add-button w-full primary" @click="newChat">
            <AppIcon iconName="app-create-chat"></AppIcon>
            <span class="ml-4">{{ $t('chat.createChat') }}</span>
          </el-button>
          <p class="mt-20 mb-8">{{ $t('chat.history') }}</p>
        </div>

        <div class="left-height pt-0">
          <el-scrollbar>
            <div>
              <common-list
                :style="{ '--el-color-primary': applicationDetail?.custom_theme?.theme_color }"
                :data="chatLogData"
                v-loading="left_loading"
                :defaultActive="currentChatId"
                @click="clickListHandle"
                @mouseenter="mouseenter"
                @mouseleave="mouseId = ''"
              >
                <template #default="{ row }">
                  <div class="flex-between">
                    <ReadWrite
                      @change="editName($event, row)"
                      :data="row.abstract"
                      trigger="manual"
                      :write="row.writeStatus"
                      @close="closeWrite(row)"
                      :maxlength="1024"
                    />
                    <div
                      @click.stop
                      v-if="mouseId === row.id && row.id !== 'new' && !row.writeStatus"
                      class="flex"
                    >
                      <el-button style="padding: 0" link @click.stop="openWrite(row)">
                        <el-icon>
                          <EditPen />
                        </el-icon>
                      </el-button>
                      <el-button style="padding: 0" link @click.stop="deleteLog(row)">
                        <el-icon>
                          <Delete />
                        </el-icon>
                      </el-button>
                    </div>
                  </div>
                </template>
                <template #empty>
                  <div class="text-center mt-24">
                    <el-text type="info">{{ $t('chat.noHistory') }}</el-text>
                  </div>
                </template>
              </common-list>
            </div>
            <div v-if="chatLogData.length" class="gradient-divider lighter mt-8">
              <span>{{ $t('chat.only20history') }}</span>
            </div>
          </el-scrollbar>
        </div>
        <div class="flex align-center user-info" @click="toUserCenter">
          <el-avatar :size="32">
            <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
          </el-avatar>
          <span v-if="chatUser.chat_profile?.authentication" class="ml-8 color-text-primary">{{
            chatUser.chatUserProfile?.nick_name
          }}</span>
        </div>
      </el-drawer>
    </div>

    <UserCenter v-model:show="userCenterDrawerShow" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { isAppIcon } from '@/utils/common'
import { hexToRgba } from '@/utils/theme'
import { MsgError } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'
import UserCenter from './component/UserCenter.vue'
import chatAPI from '@/api/chat/chat'

const { user, chatLog, chatUser } = useStore()

const AiChatRef = ref()
const loading = ref(false)
const left_loading = ref(false)
const chatLogData = ref<any[]>([])
const show = ref(false)
const props = defineProps<{
  application_profile: any
  applicationAvailable: boolean
}>()
const applicationDetail = computed({
  get: () => {
    return props.application_profile
  },
  set: (v) => {},
})
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const currentRecordList = ref<any>([])
const currentChatId = ref('new') // 当前历史记录Id 默认为'new'

const mouseId = ref('')

const customStyle = computed(() => {
  return {
    background: applicationDetail.value?.custom_theme?.theme_color,
    color: applicationDetail.value?.custom_theme?.header_font_color,
  }
})

function editName(val: string, item: any) {
  if (val) {
    const obj = {
      abstract: val,
    }

    chatLog.asyncPutChatClientLog(applicationDetail.value.id, item.id, obj, loading).then(() => {
      const find = chatLogData.value.find((row: any) => row.id === item.id)
      if (find) {
        find.abstract = val
      }
      item['writeStatus'] = false
    })
  } else {
    MsgError(t('views.applicationWorkflow.tip.nameMessage'))
  }
}

function openWrite(item: any) {
  item['writeStatus'] = true
}

function closeWrite(item: any) {
  item['writeStatus'] = false
}

function mouseenter(row: any) {
  mouseId.value = row.id
}
function deleteLog(row: any) {
  chatLog.asyncDelChatClientLog(applicationDetail.value.id, row.id, left_loading).then(() => {
    if (currentChatId.value === row.id) {
      currentChatId.value = 'new'
      paginationConfig.current_page = 1
      paginationConfig.total = 0
      currentRecordList.value = []
    }
    getChatLog(applicationDetail.value.id)
  })
}

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

const newObj = {
  id: 'new',
  abstract: t('chat.createChat'),
}
function newChat() {
  paginationConfig.current_page = 1
  currentRecordList.value = []
  if (!chatLogData.value.some((v) => v.id === 'new')) {
    chatLogData.value.unshift(newObj)
  }
  currentChatId.value = 'new'
}

function getChatLog(id: string) {
  const page = {
    current_page: 1,
    page_size: 20,
  }

  chatAPI.pageChat(page.current_page, page.page_size, left_loading).then((res: any) => {
    chatLogData.value = res.data.records
    paginationConfig.current_page = 1
    paginationConfig.total = 0
    currentRecordList.value = []
    currentChatId.value = chatLogData.value?.[0]?.id || 'new'
    if (currentChatId.value !== 'new') {
      getChatRecord()
    }
  })
}

function getChatRecord() {
  return chatAPI
    .pageChatRecord(
      currentChatId.value,
      paginationConfig.current_page,
      paginationConfig.page_size,
      loading,
    )
    .then((res: any) => {
      paginationConfig.total = res.data.total
      const list = res.data.records
      list.map((v: any) => {
        v['write_ed'] = true
        v['record_id'] = v.id
      })
      currentRecordList.value = [...list, ...currentRecordList.value].sort((a, b) =>
        a.create_time.localeCompare(b.create_time),
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
    if (currentChatId.value !== 'new') {
      getChatRecord()
    }
    show.value = false
  }
}

function refresh(id: string) {
  getChatLog(applicationDetail.value.id)
  currentChatId.value = id
}
/**
 *初始化历史对话记录
 */
const init = () => {
  getChatLog(applicationDetail.value.id)
}

onMounted(() => {
  init()
})

const userCenterDrawerShow = ref(false)
function toUserCenter() {
  if (!chatUser.chat_profile?.authentication) return
  userCenterDrawerShow.value = true
}
</script>
<style lang="scss">
.chat-mobile {
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
    padding-top: calc(var(--app-header-height) + 16px);
    height: calc(100vh - var(--app-header-height) - 16px);
    overflow: hidden;
  }
  .new-chat-button {
    z-index: 11;
    font-size: 1rem;
  }
  // 历史对话弹出层
  .left-drawer {
    .el-drawer__body {
      padding: 16px;
      background:
        linear-gradient(187.61deg, rgba(235, 241, 255, 0.5) 39.6%, rgba(231, 249, 255, 0.5) 94.3%),
        #eef1f4;
      overflow: hidden;

      .add-button {
        border: 1px solid var(--el-color-primary);
      }

      .left-height {
        height: calc(100vh - 212px);
      }

      .user-info {
        border-radius: 6px;
        padding: 4px 8px;
        margin-top: 16px;
        box-sizing: border-box;
      }
    }
  }

  // &.chat-embed--popup {
  //   .chat-popover-button {
  //     right: 85px;
  //   }
  // }

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
  // .AiChat-embed {
  //   .ai-chat__operate {
  //     padding-top: 12px;
  //   }
  // }
}
</style>
<style lang="scss" scoped>
:deep(.el-overlay) {
  background-color: transparent;
}
</style>
