<template>
  <div class="portal-chat-page h-full flex">
    <!-- Left sidebar: conversation history (same style as portal page) -->
    <aside class="portal-chat-sidebar border-r shrink-0 flex flex-col bg-white">
      <div class="p-4">
        <el-button class="w-full portal-all-btn" type="primary" @click="goBack">
          <MkIcon name="icon_magic_stick_outlined" :size="16" />
          所有智能体
        </el-button>
      </div>
      <div class="portal-history flex-1 overflow-auto px-4 pb-4">
        <div class="text-sm text-gray-400 mb-3 font-medium">对话历史</div>
        <div class="space-y-1">
          <button
            v-for="conv in conversationList"
            :key="conv.id"
            type="button"
            class="w-full text-left px-3 py-2 rounded-md text-sm truncate transition-colors"
            :class="conv.id === activeChatId ? 'bg-primary-light text-primary' : 'hover:bg-gray-100'"
            @click="switchConversation(conv)"
          >
            {{ conv.abstract || '新建对话' }}
          </button>
        </div>
        <el-empty v-if="!loadingHistory && conversationList.length === 0" description="暂无对话" :image-size="50" />
      </div>
    </aside>

    <!-- Right main: chat messages -->
    <div class="flex-1 flex flex-col bg-white">
      <!-- Chat header -->
      <div class="chat-header flex items-center gap-3 px-5 py-3 border-b shrink-0">
        <el-button text @click="goBack">
          <MkIcon name="icon_left_outlined" :size="16" />
          返回
        </el-button>
        <el-divider direction="vertical" />
        <span class="font-medium text-sm">{{ appName }}</span>
      </div>

      <!-- Messages area -->
      <el-scrollbar ref="scrollbarRef" class="flex-1" @scroll="onScroll">
        <div class="chat-messages max-w-3xl mx-auto px-4 py-6">
          <!-- Prologue card -->
          <div v-if="prologue" class="mb-6">
            <div class="flex items-start gap-3 mb-4">
              <el-avatar :size="36" shape="square" style="background:#ebf1ff">
                <span class="text-sm font-semibold" style="color:#3370ff">AI</span>
              </el-avatar>
              <div class="prologue-content">
                <div class="prologue-text text-sm leading-relaxed text-gray-700" v-html="prologueHtml"></div>
              </div>
            </div>
          </div>

          <!-- Chat records -->
          <div v-for="record in chatRecords" :key="record.id" class="mb-6">
            <!-- User message -->
            <div class="flex items-start gap-3 mb-4 justify-end">
              <div class="user-message bg-primary text-white text-sm px-4 py-2.5 rounded-xl rounded-br-sm max-w-[70%]">
                {{ record.problem_text || record.question?.content }}
              </div>
              <el-avatar :size="36">
                {{ (userStore.userInfo as any)?.nick_name?.[0] || 'U' }}
              </el-avatar>
            </div>
            <!-- AI response -->
            <div v-if="record.answer_text" class="flex items-start gap-3 mb-4">
              <el-avatar :size="36" shape="square" style="background:#ebf1ff">
                <span class="text-sm font-semibold" style="color:#3370ff">AI</span>
              </el-avatar>
              <div class="ai-message bg-gray-50 text-sm px-4 py-2.5 rounded-xl rounded-bl-sm max-w-[70%] text-gray-700">
                <div class="markdown-body" v-html="renderMarkdown(record.answer_text)"></div>
              </div>
            </div>
          </div>

          <!-- Loading indicator -->
          <div v-if="sending" class="flex items-start gap-3 mb-4">
            <el-avatar :size="36" shape="square" style="background:#ebf1ff">
              <span class="text-sm font-semibold" style="color:#3370ff">AI</span>
            </el-avatar>
            <div class="text-gray-400 text-sm py-2">思考中...</div>
          </div>
        </div>
      </el-scrollbar>

      <!-- Input area -->
      <div class="chat-input-area shrink-0 border-t bg-white px-4 py-3">
        <div class="max-w-3xl mx-auto">
          <div class="flex items-end gap-2 bg-gray-50 rounded-xl px-4 py-2 border">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="1"
              placeholder="输入您的问题..."
              :disabled="sending"
              resize="none"
              class="chat-input"
              @keydown.enter.prevent="sendMessage"
            />
            <el-button
              type="primary"
              :icon="Promotion"
              circle
              :disabled="!inputMessage.trim() || sending"
              @click="sendMessage"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Promotion } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import {
  openChatSession,
  getApplicationDetail,
  getConversationHistory,
} from '@/api/application/portal-chat'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const scrollbarRef = ref<any>(null)

const workspaceId = route.params.workspaceId as string
const applicationId = route.params.agentId as string

const appName = ref('')
const prologue = ref('')
const activeChatId = ref('')
const chatRecords = ref<any[]>([])
const conversationList = ref<any[]>([])
const inputMessage = ref('')
const sending = ref(false)
const loadingHistory = ref(false)

const prologueHtml = computed(() => {
  if (!prologue.value) return ''
  return renderMarkdown(prologue.value)
})

function renderMarkdown(text: string): string {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  html = html
    .replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>')
  return html
}

function goBack() {
  router.push({ name: 'portal' })
}

function onScroll() {
  // Handle scroll events if needed
}

async function openSession() {
  try {
    const res = await openChatSession(workspaceId, applicationId)
    activeChatId.value = res.data?.chat_id || ''
  } catch (e: any) {
    ElMessage.error(e.message || '无法打开对话')
  }
}

async function loadAppDetail() {
  try {
    const res = await getApplicationDetail(workspaceId, applicationId)
    const data = res.data
    appName.value = data.name || ''
    prologue.value = data.prologue || ''
  } catch {
    // Ignore
  }
}

async function loadConversationList() {
  loadingHistory.value = true
  try {
    const res = await getConversationHistory(workspaceId, applicationId)
    conversationList.value = res.data?.records || res.data || []
  } catch {
    // Ignore
  } finally {
    loadingHistory.value = false
  }
}

async function switchConversation(conv: any) {
  activeChatId.value = conv.id
  await loadChatMessages(conv.id)
}

async function loadChatMessages(chatId: string) {
  try {
    const { getConversationMessages } = await import('@/api/application/portal-chat')
    const res = await getConversationMessages(workspaceId, applicationId, chatId)
    chatRecords.value = res.data?.records || res.data || []
    scrollToBottom()
  } catch {
    chatRecords.value = []
  }
}

async function sendMessage() {
  const content = inputMessage.value.trim()
  if (!content || sending.value) return

  // If no active session, open one first
  if (!activeChatId.value) {
    try {
      const res = await openChatSession(workspaceId, applicationId)
      activeChatId.value = res.data?.chat_id || ''
    } catch (e: any) {
      ElMessage.error(e.message || '无法打开对话')
      return
    }
  }

  // Add user message to local state immediately
  const userMsg: any = {
    id: `temp-${Date.now()}`,
    problem_text: content,
    answer_text: '',
    isTemp: true,
  }
  chatRecords.value.push(userMsg)
  inputMessage.value = ''
  scrollToBottom()

  sending.value = true
  try {
    const { sendChatMessage } = await import('@/api/application/portal-chat')
    const res = await sendChatMessage(activeChatId.value, content)

    // Replace temp msg with real data
    const idx = chatRecords.value.indexOf(userMsg)
    if (idx !== -1) {
      chatRecords.value[idx] = {
        ...res.data,
        problem_text: content,
      }
    }
    scrollToBottom()
    loadConversationList()
  } catch (e: any) {
    ElMessage.error(e.message || '发送失败')
    // Remove temp message on failure
    chatRecords.value = chatRecords.value.filter((r) => r.id !== userMsg.id)
  } finally {
    sending.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    const el = scrollbarRef.value?.wrapRef
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  })
}

onMounted(async () => {
  await loadAppDetail()
  await loadConversationList()
})
</script>

<style scoped lang="scss">
.portal-chat-page {
  height: 100%;
}

.portal-chat-sidebar {
  width: 200px;
  height: 100%;
}

.portal-all-btn { border-radius: 8px; }

.portal-history {
  .el-empty { padding: 20px 0; }
}

.chat-header {
  height: 50px;
}

.chat-messages {
  min-height: 100%;
}

.prologue-text {
  line-height: 1.7;
}

.prologue-content {
  background: #f9fafb;
  border-radius: 12px;
  padding: 12px 16px;
  max-width: 70%;
}

.user-message {
  line-height: 1.5;
  word-break: break-word;
}

.ai-message {
  line-height: 1.5;
  word-break: break-word;
}

.chat-input {
  textarea {
    border: none;
    background: transparent;
    resize: none;
    min-height: 22px;
    max-height: 120px;
    font-size: 14px;
    box-shadow: none;

    &:focus {
      box-shadow: none;
    }
  }
}
</style>

<style>
.chat-input .el-textarea__inner {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0;
  min-height: 22px;
  line-height: 1.5;
}
.chat-input .el-textarea__inner:focus {
  box-shadow: none !important;
}
</style>
