<template>
  <div
    class="chat-pc"
    :class="classObj"
    v-loading="loading"
    :style="{
      '--el-color-primary': applicationDetail?.custom_theme?.theme_color,
      '--el-color-primary-light-9': hexToRgba(applicationDetail?.custom_theme?.theme_color, 0.1),
    }"
  >
    <div class="flex h-full w-full">
      <div class="chat-pc__left">
        <el-menu
          class="w-full h-full"
          :default-active="currentChatId"
          :collapse="isPcCollapse"
          collapse-transition
          popper-class="chat-pc-popper"
        >
          <div style="padding: 16px 18px 0 18px">
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
              <h4 v-show="!isPcCollapse">{{ applicationDetail?.name }}</h4>
            </div>
            <el-button
              type="primary"
              plain
              v-show="!isPcCollapse"
              class="add-button w-full primary"
              @click="newChat"
            >
              <AppIcon iconName="app-create-chat"></AppIcon>
              <span class="ml-4">{{ $t('chat.createChat') }}</span>
            </el-button>
            <p v-show="!isPcCollapse" class="mt-20 mb-8">{{ $t('chat.history') }}</p>
          </div>
          <div v-show="!isPcCollapse" class="left-height pt-0">
            <el-scrollbar>
              <div class="p-8 pt-0">
                <common-list
                  :style="{
                    '--el-color-primary': applicationDetail?.custom_theme?.theme_color,
                    '--el-color-primary-light-9': hexToRgba(
                      applicationDetail?.custom_theme?.theme_color,
                      0.1,
                    ),
                  }"
                  :data="chatLogData"
                  class="mt-8"
                  v-loading="left_loading"
                  :defaultActive="currentChatId"
                  @click="clickListHandle"
                  @mouseenter="mouseenter"
                  @mouseleave="mouseId = ''"
                >
                  <template #default="{ row }">
                    <div class="flex-between">
                      <span :title="row.abstract">
                        {{ row.abstract }}
                      </span>
                      <div @click.stop v-show="mouseId === row.id && row.id !== 'new'">
                        <el-dropdown trigger="click" :teleported="false">
                          <el-button text>
                            <el-icon><MoreFilled /></el-icon>
                          </el-button>

                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item @click.stop="editLogTitle(row)">
                                <el-icon><EditPen /></el-icon>
                                {{ $t('common.edit') }}
                              </el-dropdown-item>
                              <el-dropdown-item @click.stop="deleteLog(row)">
                                <el-icon><Delete /></el-icon>
                                {{ $t('common.delete') }}
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
                  </template>

                  <template #empty>
                    <div class="text-center">
                      <el-text type="info">{{ $t('chat.noHistory') }}</el-text>
                    </div>
                  </template>
                </common-list>
              </div>
              <div v-if="chatLogData?.length" class="gradient-divider lighter mt-8">
                <span>{{ $t('chat.only20history') }}</span>
              </div>
            </el-scrollbar>
          </div>
          <el-menu-item index="1" v-show="isPcCollapse" @click="newChat">
            <AppIcon iconName="app-create-chat"></AppIcon>
            <template #title>{{ $t('chat.createChat') }}</template>
          </el-menu-item>
          <el-sub-menu v-show="isPcCollapse" index="2">
            <template #title>
              <el-icon>
                <location />
              </el-icon>
            </template>
            <el-menu-item-group v-loading="left_loading">
              <template #title
                ><span>{{ $t('chat.history') }}</span></template
              >
              <el-menu-item
                v-for="row in chatLogData"
                :index="row.id"
                :key="row.id"
                @click="clickListHandle(row)"
              >
                <div class="flex-between w-full lighter">
                  <span :title="row.abstract">
                    {{ row.abstract }}
                  </span>
                  <div @click.stop class="flex" v-show="mouseId === row.id && row.id !== 'new'">
                    <el-dropdown trigger="click" :teleported="false">
                      <el-icon class="rotate-90 mt-4">
                        <MoreFilled />
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click.stop="editLogTitle(row)">
                            <el-icon>
                              <EditPen />
                            </el-icon>
                            {{ $t('common.edit') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click.stop="deleteLog(row)">
                            <el-icon>
                              <Delete />
                            </el-icon>
                            {{ $t('common.delete') }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </el-menu-item>
            </el-menu-item-group>
            <div v-if="!chatLogData?.length" class="text-center">
              <el-text type="info">{{ $t('chat.noHistory') }}</el-text>
            </div>
          </el-sub-menu>

          <div v-if="!chatUser.chat_profile?.authentication" class="no-auth-avatar">
            <el-avatar :size="32">
              <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
            </el-avatar>
          </div>
          <el-dropdown v-else trigger="click" type="primary" class="w-full">
            <div class="flex align-center user-info">
              <el-avatar :size="32">
                <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
              </el-avatar>
              <span v-show="!isPcCollapse" class="ml-8 color-text-primary">{{
                chatUser.chatUserProfile?.nick_name
              }}</span>
            </div>

            <template #dropdown>
              <el-dropdown-menu class="avatar-dropdown">
                <div class="flex align-center" style="padding: 8px 12px">
                  <div class="mr-8 flex align-center">
                    <el-avatar :size="40">
                      <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
                    </el-avatar>
                  </div>
                  <div>
                    <h4 class="medium mb-4">{{ chatUser.chatUserProfile?.nick_name }}</h4>
                    <div class="color-secondary">
                      {{ `${t('common.username')}: ${chatUser.chatUserProfile?.username}` }}
                    </div>
                  </div>
                </div>
                <el-dropdown-item
                  v-if="chatUser.chatUserProfile?.source === 'LOCAL'"
                  class="border-t"
                  style="padding-top: 8px; padding-bottom: 8px"
                  @click="openResetPassword"
                >
                  <AppIcon iconName="app-export" />
                  {{ $t('views.login.resetPassword') }}
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="chatUser.chatUserProfile?.source === 'LOCAL'"
                  class="border-t"
                  style="padding-top: 8px; padding-bottom: 8px"
                  @click="logout"
                >
                  <AppIcon iconName="app-export" />
                  {{ $t('layout.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-menu>
        <el-button
          v-if="!common.isMobile()"
          class="pc-collapse cursor"
          circle
          @click="isPcCollapse = !isPcCollapse"
        >
          <el-icon>
            <component :is="isPcCollapse ? 'ArrowRightBold' : 'ArrowLeftBold'" />
          </el-icon>
        </el-button>
      </div>
      <div
        class="chat-pc__right chat-background"
        :style="{ backgroundImage: `url(${applicationDetail?.chat_background})` }"
      >
        <el-splitter>
          <el-splitter-panel>
            <div class="mb-24 p-16-24 flex-between">
              <h4 class="ellipsis-1" style="width: 66%">
                {{ currentChatName }}
              </h4>

              <span class="flex align-center" v-if="currentRecordList.length">
                <AppIcon
                  v-if="paginationConfig.total"
                  iconName="app-chat-record"
                  class="color-secondary mr-8"
                  style="font-size: 16px"
                ></AppIcon>
                <span v-if="paginationConfig.total" class="lighter">
                  {{ paginationConfig.total }} {{ $t('chat.question_count') }}
                </span>
                <el-dropdown class="ml-8">
                  <AppIcon
                    iconName="app-export"
                    class="cursor"
                    :title="$t('chat.exportRecords')"
                  ></AppIcon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="exportMarkdown"
                        >{{ $t('common.export') }} Markdown</el-dropdown-item
                      >
                      <el-dropdown-item @click="exportHTML"
                        >{{ $t('common.export') }} HTML</el-dropdown-item
                      >
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </span>
            </div>
            <div class="right-height chat-width">
              <AiChat
                ref="AiChatRef"
                v-model:applicationDetails="applicationDetail"
                :available="applicationAvailable"
                type="ai-chat"
                :appId="applicationDetail?.id"
                :record="currentRecordList"
                :chatId="currentChatId"
                executionIsRightPanel
                @refresh="refresh"
                @scroll="handleScroll"
                @open-execution-detail="openExecutionDetail"
                @openParagraph="openKnowledgeSource"
              >
              </AiChat>
            </div>
          </el-splitter-panel>
          <el-splitter-panel
            class="execution-detail-panel"
            v-model:size="rightPanelSize"
            :resizable="false"
            collapsible
          >
            <div class="p-16 flex-between border-b">
              <h4 class="medium">{{ rightPanelTitle }}</h4>
              <el-icon size="20" class="cursor" @click="closeExecutionDetail"><Close /></el-icon>
            </div>
            <div class="execution-detail-content" v-loading="rightPanelLoading">
              <ParagraphSourceContent
                v-if="rightPanelType === 'knowledgeSource'"
                :detail="rightPanelDetail"
              />
              <ExecutionDetailContent
                v-if="rightPanelType === 'executionDetail'"
                :detail="executionDetail"
                :type="applicationDetail?.type"
              />
            </div>
          </el-splitter-panel>
        </el-splitter>
      </div>
    </div>

    <EditTitleDialog ref="EditTitleDialogRef" @refresh="refreshFieldTitle" />
    <ResetPassword
      ref="resetPasswordRef"
      emitConfirm
      @confirm="handleResetPassword"
    ></ResetPassword>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { marked } from 'marked'
import { saveAs } from 'file-saver'
import chatAPI from '@/api/chat/chat'
import { isAppIcon } from '@/utils/common'
import useStore from '@/stores'
import useResize from '@/layout/hooks/useResize'
import { hexToRgba } from '@/utils/theme'
import EditTitleDialog from './EditTitleDialog.vue'
import { useRouter } from 'vue-router'
import ResetPassword from '@/layout/layout-header/avatar/ResetPassword.vue'
import { t } from '@/locales'
import type { ResetCurrentUserPasswordRequest } from '@/api/type/user'
import ExecutionDetailContent from '@/components/ai-chat/component/ExecutionDetailContent.vue'
import ParagraphSourceContent from '@/components/ai-chat/component/ParagraphSourceContent.vue'
import { cloneDeep } from 'lodash'

useResize()

const { common, chatUser } = useStore()
const router = useRouter()

const EditTitleDialogRef = ref()

const isCollapse = ref(false)
const isPcCollapse = ref(false)
watch(
  () => common.device,
  () => {
    if (common.isMobile()) {
      isPcCollapse.value = false
    }
  },
)

const logout = () => {
  chatUser.logout().then(() => {
    router.push({ name: 'login' })
  })
}

const resetPasswordRef = ref<InstanceType<typeof ResetPassword>>()
const openResetPassword = () => {
  resetPasswordRef.value?.open()
}

const handleResetPassword = (param: ResetCurrentUserPasswordRequest) => {
  chatAPI.resetCurrentPassword(param).then(() => {
    logout()
  })
}

const classObj = computed(() => {
  return {
    mobile: common.isMobile(),
    hideLeft: !isCollapse.value,
    openLeft: isCollapse.value,
  }
})

const newObj = {
  id: 'new',
  abstract: t('chat.createChat'),
}
const props = defineProps<{
  application_profile: any
  applicationAvailable: boolean
}>()
const AiChatRef = ref()
const loading = ref(false)
const left_loading = ref(false)

const applicationDetail = computed({
  get: () => {
    return props.application_profile
  },
  set: (v) => {},
})

const chatLogData = ref<any[]>([])

const paginationConfig = ref({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const currentRecordList = ref<any>([])
const currentChatId = ref('new') // 当前历史记录Id 默认为'new'
const currentChatName = ref(t('chat.createChat'))
const mouseId = ref('')

function mouseenter(row: any) {
  mouseId.value = row.id
}

function editLogTitle(row: any) {
  EditTitleDialogRef.value.open(row, applicationDetail.value.id)
}
function refreshFieldTitle(chatId: string, abstract: string) {
  const find = chatLogData.value.find((item: any) => item.id == chatId)
  if (find) {
    find.abstract = abstract
  }
}
function deleteLog(row: any) {
  chatAPI.deleteChat(row.id, left_loading).then(() => {
    if (currentChatId.value === row.id) {
      currentChatId.value = 'new'
      currentChatName.value = t('chat.createChat')
      paginationConfig.value.current_page = 1
      paginationConfig.value.total = 0
      currentRecordList.value = []
    }
    getChatLog(applicationDetail.value.id)
  })
}

function handleScroll(event: any) {
  if (
    currentChatId.value !== 'new' &&
    event.scrollTop === 0 &&
    paginationConfig.value.total > currentRecordList.value.length
  ) {
    const history_height = event.dialogScrollbar.offsetHeight
    paginationConfig.value.current_page += 1
    getChatRecord().then(() => {
      event.scrollDiv.setScrollTop(event.dialogScrollbar.offsetHeight - history_height)
    })
  }
}

function newChat() {
  if (!chatLogData.value.some((v) => v.id === 'new')) {
    paginationConfig.value.current_page = 1
    paginationConfig.value.total = 0
    currentRecordList.value = []
    chatLogData.value.unshift(newObj)
  } else {
    paginationConfig.value.current_page = 1
    paginationConfig.value.total = 0
    currentRecordList.value = []
  }
  currentChatId.value = 'new'
  currentChatName.value = t('chat.createChat')
  if (common.isMobile()) {
    isCollapse.value = false
  }
}

function getChatLog(id: string, refresh?: boolean) {
  const page = {
    current_page: 1,
    page_size: 20,
  }

  chatAPI.pageChat(page.current_page, page.page_size, left_loading).then((res: any) => {
    chatLogData.value = res.data.records
    if (refresh) {
      currentChatName.value = chatLogData.value?.[0]?.abstract
    } else {
      paginationConfig.value.current_page = 1
      paginationConfig.value.total = 0
      currentRecordList.value = []
      currentChatId.value = chatLogData.value?.[0]?.id || 'new'
      currentChatName.value = chatLogData.value?.[0]?.abstract || t('chat.createChat')
      if (currentChatId.value !== 'new') {
        getChatRecord()
      }
    }
  })
}

function getChatRecord() {
  return chatAPI
    .pageChatRecord(
      currentChatId.value,
      paginationConfig.value.current_page,
      paginationConfig.value.page_size,
      loading,
    )
    .then((res: any) => {
      paginationConfig.value.total = res.data.total
      const list = res.data.records
      list.map((v: any) => {
        v['write_ed'] = true
        v['record_id'] = v.id
      })
      currentRecordList.value = [...list, ...currentRecordList.value].sort((a, b) =>
        a.create_time.localeCompare(b.create_time),
      )
      if (paginationConfig.value.current_page === 1) {
        nextTick(() => {
          // 将滚动条滚动到最下面
          AiChatRef.value.setScrollBottom()
        })
      }
    })
}

const clickListHandle = (item: any) => {
  if (item.id !== currentChatId.value) {
    paginationConfig.value.current_page = 1
    paginationConfig.value.total = 0
    currentRecordList.value = []
    currentChatId.value = item.id
    currentChatName.value = item.abstract
    if (currentChatId.value !== 'new') {
      getChatRecord()

      // 切换对话后，取消暂停的浏览器播放
      if (window.speechSynthesis.paused && window.speechSynthesis.speaking) {
        window.speechSynthesis.resume()
        nextTick(() => {
          window.speechSynthesis.cancel()
        })
      }
    }
  }
  if (common.isMobile()) {
    isCollapse.value = false
  }
}

function refresh(id: string) {
  getChatLog(applicationDetail.value.id, true)
  currentChatId.value = id
}

async function exportMarkdown(): Promise<void> {
  const suggestedName: string = `${currentChatId.value}.md`
  const markdownContent: string = currentRecordList.value
    .map((record: any) => `# ${record.problem_text}\n\n${record.answer_text}\n\n`)
    .join('\n')

  const blob: Blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' })
  saveAs(blob, suggestedName)
}

async function exportHTML(): Promise<void> {
  const suggestedName: string = `${currentChatId.value}.html`
  const markdownContent: string = currentRecordList.value
    .map((record: any) => `# ${record.problem_text}\n\n${record.answer_text}\n\n`)
    .join('\n')
  const htmlContent: any = marked(markdownContent)

  const blob: Blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' })
  saveAs(blob, suggestedName)
}

/**
 *初始化历史对话记录
 */
const init = () => {
  getChatLog(applicationDetail.value?.id)
}
onMounted(() => {
  init()
})

const rightPanelSize = ref(0)
const rightPanelTitle = ref('')
const rightPanelType = ref('')
const rightPanelLoading = ref(false)
const executionDetail = ref<any[]>([])
const rightPanelDetail = ref<any>()
async function openExecutionDetail(row: any) {
  rightPanelSize.value = 400
  rightPanelTitle.value = t('chat.executionDetails.title')
  rightPanelType.value = 'executionDetail'
  if (row.execution_details) {
    executionDetail.value = cloneDeep(row.execution_details)
  } else {
    const res = await chatAPI.getChatRecord(row.chat_id, row.record_id, rightPanelLoading)
    executionDetail.value = cloneDeep(res.data.execution_details)
  }
}

async function openKnowledgeSource(row: any) {
  rightPanelTitle.value = t('chat.KnowledgeSource.title')
  rightPanelType.value = 'knowledgeSource'
  // TODO 数据
  rightPanelDetail.value = row
  rightPanelSize.value = 400
}

function closeExecutionDetail() {
  rightPanelSize.value = 0
}
</script>
<style lang="scss">
.chat-pc {
  height: 100%;
  overflow: hidden;
  background: #eef1f4;

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
    position: relative;
    z-index: 1;

    .el-menu {
      display: flex;
      flex-direction: column;
      background:
        linear-gradient(187.61deg, rgba(235, 241, 255, 0.5) 39.6%, rgba(231, 249, 255, 0.5) 94.3%),
        #eef1f4;

      &:not(.el-menu--collapse) {
        width: 280px;
      }

      .el-menu-item:hover {
        background: transparent;
      }

      .no-auth-avatar {
        margin-top: auto;
        padding: 16px;
        .el-avatar {
          cursor: default;
        }
      }

      .el-dropdown {
        margin-top: auto;
        .user-info {
          width: 100%;
          cursor: pointer;
          border-radius: 6px;
          padding: 4px 8px;
          margin: 16px;
          box-sizing: border-box;
          &:hover {
            background-color: #1f23291a;
          }
        }
      }

      &.el-menu--collapse {
        .el-menu-item,
        .el-menu-tooltip__trigger,
        .el-sub-menu__title {
          padding: 0;
        }

        .el-menu-item .el-menu-tooltip__trigger,
        .el-sub-menu__title {
          position: static;
          width: 40px;
          height: 40px;
          border-radius: 6px;
          align-items: center;
          justify-content: center;
          margin: 0 auto;
        }

        .el-menu-item:hover .el-menu-tooltip__trigger,
        .el-sub-menu__title:hover {
          background-color: #1f23291a;
        }

        .user-info {
          margin: 16px 8px;
        }
      }
    }

    .add-button {
      border: 1px solid var(--el-color-primary);
    }

    .left-height {
      height: calc(100vh - 212px);
    }

    .pc-collapse {
      position: absolute;
      top: 20px;
      right: -15px;
      box-shadow: 0px 5px 10px 0px #1f23291a;
    }
  }

  &__right {
    flex: 1;
    overflow: hidden;
    position: relative;
    box-sizing: border-box;

    .right-height {
      height: calc(100vh - 85px);
    }

    .el-splitter-bar__collapse-icon,
    .el-splitter-bar__dragger {
      display: none;
    }
    .execution-detail-panel {
      background: #ffffff;
      height: 100%;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      .execution-detail-content {
        flex: 1;
        overflow: hidden;
        .execution-details {
          padding: 16px;
        }
      }
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

  .collapse {
    display: none;
  }
}

.chat-pc-popper {
  .el-menu-item-group__title {
    padding-bottom: 16px;
    font-weight: 500;
    color: var(--app-text-color-secondary);
  }
  .el-menu-item {
    border-radius: 6px;
    height: 40px;
    margin: 0 8px;
    padding-left: 8px;
    padding-right: 8px;
    &:hover {
      background-color: #1f23291a;
    }
    &.is-active {
      background-color: #3370ff1a;
    }
  }
}
// 适配移动端
.mobile {
  .chat-pc {
    &__right {
      width: 100%;
    }
    &__left {
      display: none;
      width: 0;
    }
  }
  .collapse {
    display: block;
    position: fixed;
    bottom: 90px;
    z-index: 99;
  }
  &.openLeft {
    .chat-pc {
      &__left {
        display: block;
        position: fixed;
        width: 100%;
        z-index: 99;
        height: calc(100vh);
        .el-menu {
          width: 100%;
        }
      }
    }
    .collapse {
      display: block;
      position: absolute;
      bottom: 90px;
      right: 0;
      z-index: 99;
    }
  }
}

.chat-width {
  max-width: 80%;
  margin: 0 auto;
}
@media only screen and (max-width: 1000px) {
  .chat-width {
    max-width: 100% !important;
    margin: 0 auto;
  }
}
</style>

<style lang="scss" scoped>
.avatar-dropdown {
  min-width: 240px;
}
</style>
