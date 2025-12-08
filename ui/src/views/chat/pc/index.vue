<template>
  <div
    class="chat-pc"
    :class="classObj"
    v-loading="loading"
    :style="{
      '--el-color-primary': applicationDetail?.custom_theme?.theme_color,
      '--el-color-primary-light-9': hexToRgba(
        applicationDetail?.custom_theme?.theme_color || '#3370FF',
        0.1,
      ),
      '--el-color-primary-light-6': hexToRgba(
        applicationDetail?.custom_theme?.theme_color || '#3370FF',
        0.4,
      ),
      '--el-color-primary-light-06': hexToRgba(
        applicationDetail?.custom_theme?.theme_color || '#3370FF',
        0.04,
      ),
    }"
  >
    <div class="flex h-full w-full">
      <div class="chat-pc__left">
        <HistoryPanel
          :application-detail="applicationDetail"
          :chat-log-data="chatLogData"
          :left-loading="left_loading"
          :currentChatId="currentChatId"
          @new-chat="newChat"
          @clickLog="clickListHandle"
          @delete-log="deleteLog"
          @clear-chat="clearChat"
          @refreshFieldTitle="refreshFieldTitle"
          :isPcCollapse="isPcCollapse"
        >
          <div class="user-info p-16 cursor">
            <el-avatar
              :size="32"
              v-if="
                !chatUser.chat_profile?.authentication ||
                chatUser.chat_profile.authentication_type === 'password'
              "
            >
              <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
            </el-avatar>
            <el-dropdown v-else trigger="click" type="primary" class="w-full">
              <div class="flex align-center">
                <el-avatar :size="32">
                  <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
                </el-avatar>
                <span v-show="!isPcCollapse" class="ml-8 color-text-primary">{{
                  chatUser.chatUserProfile?.nick_name
                }}</span>
              </div>

              <template #dropdown>
                <el-dropdown-menu style="min-width: 260px">
                  <div class="flex align-center p-8">
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
                    <AppIcon iconName="app-key" class="color-secondary"></AppIcon>
                    {{ $t('views.login.resetPassword') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="chatUser.chatUserProfile?.source === 'LOCAL'"
                    class="border-t"
                    style="padding-top: 8px; padding-bottom: 8px"
                    @click="logout"
                  >
                    <AppIcon iconName="app-export" class="color-secondary" />
                    {{ $t('layout.logout') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </HistoryPanel>
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
        :style="{
          backgroundImage: `url(${applicationDetail?.chat_background})`,
          '--execution-detail-panel-width': rightPanelSize + 'px',
        }"
      >
        <div style="flex: 1; width: calc(100% - var(--execution-detail-panel-width))">
          <div class="p-16-24 flex-between">
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
                    <el-dropdown-item @click="openPDFExport"
                      >{{ $t('common.export') }} PDF</el-dropdown-item
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
              @openParagraphDocument="openParagraphDocument"
            >
            </AiChat>
          </div>
        </div>
        <div class="execution-detail-panel" :resizable="false" collapsible>
          <div class="p-16 flex-between border-b">
            <h4 class="medium ellipsis" :title="rightPanelTitle">{{ rightPanelTitle }}</h4>

            <div class="flex align-center">
              <span v-if="rightPanelType === 'paragraphDocument'" class="mr-4">
                <a
                  :href="
                    getFileUrl(rightPanelDetail?.meta?.source_file_id) ||
                    rightPanelDetail?.meta?.source_url
                  "
                  target="_blank"
                  class="ellipsis-1"
                  :title="rightPanelDetail?.document_name?.trim()"
                >
                  <el-button text>
                    <AppIcon iconName="app-pdf-export" class="cursor"></AppIcon>
                  </el-button>
                </a>
              </span>
              <!-- <span v-if="rightPanelType === 'paragraphDocument'">
                <el-button text> <app-icon iconName="app-export" size="20" /></el-button>
              </span> -->
              <span>
                <el-button text @click="closeExecutionDetail">
                  <el-icon size="20"><Close /></el-icon
                ></el-button>
              </span>
            </div>
          </div>
          <div class="execution-detail-content" v-loading="rightPanelLoading">
            <ParagraphSourceContent
              v-if="rightPanelType === 'knowledgeSource'"
              :detail="rightPanelDetail"
            />
            <ExecutionDetailContent
              v-if="rightPanelType === 'executionDetail'"
              :detail="executionDetail"
              :appType="applicationDetail?.type"
            />
            <ParagraphDocumentContent :detail="rightPanelDetail" v-else />
          </div>
        </div>
      </div>
    </div>

    <ResetPassword
      ref="resetPasswordRef"
      emitConfirm
      @confirm="handleResetPassword"
    ></ResetPassword>
    <PdfExport ref="pdfExportRef"></PdfExport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { marked } from 'marked'
import { saveAs } from 'file-saver'
import chatAPI from '@/api/chat/chat'
import useStore from '@/stores'
import useResize from '@/layout/hooks/useResize'
import { hexToRgba } from '@/utils/theme'
import { useRoute, useRouter } from 'vue-router'
import ResetPassword from '@/layout/layout-header/avatar/ResetPassword.vue'
import { t } from '@/locales'
import type { ResetCurrentUserPasswordRequest } from '@/api/type/user'
import ExecutionDetailContent from '@/components/ai-chat/component/knowledge-source-component/ExecutionDetailContent.vue'
import ParagraphSourceContent from '@/components/ai-chat/component/knowledge-source-component/ParagraphSourceContent.vue'
import ParagraphDocumentContent from '@/components/ai-chat/component/knowledge-source-component/ParagraphDocumentContent.vue'
import HistoryPanel from '@/views/chat/component/HistoryPanel.vue'
import { cloneDeep } from 'lodash'
import { getFileUrl } from '@/utils/common'
import PdfExport from '@/components/pdf-export/index.vue'

useResize()
const pdfExportRef = ref<InstanceType<typeof PdfExport>>()
const { common, chatUser } = useStore()
const router = useRouter()
const openPDFExport = () => {
  pdfExportRef.value?.open(document.getElementById('chatListId'))
}
const route = useRoute()
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
    router.push({
      name: 'login',
      query: route.query,
    })
  })
}

const resetPasswordRef = ref<InstanceType<typeof ResetPassword>>()
const openResetPassword = () => {
  resetPasswordRef.value?.open()
}

const handleResetPassword = (param: ResetCurrentUserPasswordRequest) => {
  chatAPI.resetCurrentPassword(param).then(() => {
    router.push({ name: 'login' })
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

function refreshFieldTitle(chatId: string, abstract: string) {
  const find = chatLogData.value.find((item: any) => item.id == chatId)
  if (find) {
    find.abstract = abstract
  }
}

function deleteLog(row: any) {
  chatAPI.deleteChat(row.id).then(() => {
    if (currentChatId.value === row.id) {
      currentChatId.value = 'new'
      currentChatName.value = t('chat.createChat')
      paginationConfig.value.current_page = 1
      paginationConfig.value.total = 0
      currentRecordList.value = []
    }
    chatLogData.value = chatLogData.value.filter((item) => item.id !== row.id)
  })
}

function clearChat() {
  chatAPI.clearChat(left_loading).then(() => {
    currentChatId.value = 'new'
    currentChatName.value = t('chat.createChat')
    paginationConfig.value.current_page = 1
    paginationConfig.value.total = 0
    currentRecordList.value = []
    getChatLog()
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
  closeExecutionDetail()
  currentChatId.value = 'new'
  currentChatName.value = t('chat.createChat')
  if (common.isMobile()) {
    isCollapse.value = false
  }
}

function getChatLog(refresh?: boolean) {
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
      currentChatId.value = 'new'
      currentChatName.value = t('chat.createChat')
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
    closeExecutionDetail()
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
  currentChatId.value = id
  getChatLog(true)
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
  getChatLog()
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
  rightPanelDetail.value = row
  rightPanelSize.value = 400
}

function openParagraphDocument(detail: any, row: any) {
  rightPanelTitle.value = row.document_name
  rightPanelType.value = 'paragraphDocument'
  rightPanelSize.value = 400
  rightPanelDetail.value = row
}

function closeExecutionDetail() {
  rightPanelSize.value = 0
}
</script>
<style lang="scss" scoped>
.chat-pc {
  height: 100%;
  overflow: hidden;
  background: #eef1f4;

  &__left {
    position: relative;
    z-index: 1;

    .pc-collapse {
      position: absolute;
      top: 20px;
      right: -13px;
      box-shadow: 0px 5px 10px 0px var(--app-text-color-light-1);
      z-index: 1;
      width: 24px;
      height: 24px;
    }
  }

  &__right {
    flex: 1;
    overflow: hidden;
    position: relative;
    box-sizing: border-box;
    display: flex;

    .right-height {
      height: calc(100vh - 60px);
    }

    :deep(.execution-detail-panel) {
      transition: width 0.4s;
      background: #ffffff;
      height: 100%;
      overflow: hidden;

      .execution-detail-content {
        flex: 1;
        overflow: hidden;
        height: calc(100% - 63px);

        .execution-details {
          padding: 16px;
        }
      }
    }
  }
}

.chat-width {
  max-width: 80%;
  margin: 0 auto;
}

.chat-pc__right {
  width: calc(100vw - 280px);
  --execution-detail-panel-width: 400px;

  .execution-detail-panel {
    width: var(--execution-detail-panel-width, 400px);
  }
}

@media only screen and (max-width: 1000px) {
  .chat-width {
    max-width: 100% !important;
    margin: 0 auto;
  }
}
</style>
