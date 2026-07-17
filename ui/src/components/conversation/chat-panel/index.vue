<template>
  <main class="chat-panel">
    <header class="panel-header">
      <button class="header-btn" @click="chat.toggleSidebar?.()">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
      </button>
      <div class="header-info">
        <img v-if="icon" :src="icon" class="header-icon" />
        <span class="header-title">{{ title || '新对话' }}</span>
      </div>
      <slot name="header" />
    </header>

    <div ref="msgBoxRef" class="panel-messages" @scroll="onScroll">
      <div v-if="chat.messages.value.length === 0 && !chat.msgLoading.value" class="welcome">
        <p class="welcome-title">AI 助手</p>
        <p class="welcome-sub">有什么可以帮你的？</p>
      </div>

      <template v-else>
        <div
          v-for="(msg, i) in chat.messages.value"
          :key="msg.id || i"
          :class="['msg-row', msg.role === 'USER' ? 'user' : 'assistant']"
        >
          <ContentList :content-list="msg.content" />
        </div>

        <div v-if="chat.streamLoading.value" class="msg-row assistant">
          <Loading :size="18" />
        </div>
      </template>
    </div>

    <footer class="panel-input">
      <div class="input-wrapper" :class="{ focused }">
        <textarea
          ref="inputRef"
          v-model="question.content"
          :disabled="chat.streamLoading.value"
          :placeholder="chat.streamLoading.value ? '正在回复中...' : '输入消息...'"
          @keydown="onKeydown"
          @focus="focused = true"
          @blur="focused = false"
          rows="1"
        />
        <button
          v-if="!chat.streamLoading.value"
          class="send-btn"
          :class="{ active: hasContent }"
          :disabled="!hasContent"
          @click="conversation(question)"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 14V2M3 7l5-5 5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button v-else class="send-btn stop" @click="chat.stopStream()">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="2" y="2" width="10" height="10" rx="2" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, inject, reactive } from 'vue'
import ContentList from '../content-list/index.vue'
import Loading from '../loading/index.vue'
import { Scroll, aggregators } from '../index'

const props = defineProps<{
  icon?: string
  title?: string
}>()

const chat = inject<any>('chat')

const focused = ref(false)
const question = ref<any>({ content: '' })
const inputRef = ref<HTMLTextAreaElement | null>(null)
const msgBoxRef = ref<HTMLElement | null>(null)

let scroll: InstanceType<typeof Scroll> | null = null

const hasContent = computed(() => question.value.content.trim())

// ── 创建 AI 占位消息 ──────────────────────────────────
const createAnswerMessage = () => reactive({
  role: 'ASSISTANT' as const,
  content: reactive([] as any[]),
  id: '',
  write_ed: false,
})

// ── 流式聚合 ──────────────────────────────────────────
const getOnStream = (message: any) => {
  const indexList: string[] = Array.isArray(message.content)
    ? message.content.map((c: any) => c.id + '_' + c.type)
    : []

  return (chunk: any) => {
    console.log('[onStream] chunk:', chunk)
    console.log('[onStream] message.content before:', JSON.stringify(message.content))

    if (!Array.isArray(chunk.content)) {
      console.log('[onStream] chunk.content is not array:', chunk.content)
      return
    }

    chunk.content.forEach((content: any) => {
      const id = content.id + '_' + content.type
      let i = indexList.indexOf(id)

      if (i < 0) {
        i = indexList.length
        indexList.push(id)
      }

      if (i < message.content.length) {
        const aggregated = aggregators[content.type]?.(message.content[i], content)
        console.log('[onStream] aggregated:', aggregated)
        if (aggregated) {
          message.content[i] = aggregated
        }
      } else {
        const newItem = aggregators[content.type]?.({}, content) || content
        console.log('[onStream] new item:', newItem)
        message.content.push(newItem)
      }
    })

    console.log('[onStream] message.content after:', JSON.stringify(message.content))
    scroll?.scrollBottom()
  }
}

// ── 主发送函数 ────────────────────────────────────────
const conversation = async (q: any) => {
  if (!q.content?.trim() && !hasContent.value) return
  if (chat.streamLoading.value) return

  if (!chat.currentConversation.value) {
    await chat.openChat()
    await nextTick()
  }

  chat.pushMessage({
    role: 'USER',
    content: [{ type: 'QUESTION', content: q.content }],
    id: '',
  })

  chat.pushMessage(createAnswerMessage())
  const aiMsg = chat.messages.value[chat.messages.value.length - 1]

  chat.startStream({
    cid: chat.currentChatId.value,
    request: () => chat.chat(chat.currentChatId.value, {
      message: q.content,
      stream: true,
      re_chat: false,
    }),
    onStream: getOnStream(aiMsg),
    onFinish: () => {},
  })

  question.value.content = ''
}

// ── 键盘 ──────────────────────────────────────────────
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    conversation(question.value)
  }
}

// ── 滚动 ──────────────────────────────────────────────
const onScroll = async () => {
  const el = msgBoxRef.value
  if (!el || el.scrollTop > 60) return
  if (!chat.hasMoreMsg?.value || chat.msgLoading.value) return
  await chat.loadMoreMessages?.()
}

const scrollToBottom = () => {
  scroll?.forceBottom()
}

onMounted(() => {
  if (msgBoxRef.value) {
    scroll = new Scroll(msgBoxRef.value)
  }
})

watch(() => chat?.messages?.value?.length, () => {
  nextTick(() => scroll?.scrollBottom())
})

defineExpose({ scrollToBottom, conversation })
</script>

<style scoped>
.chat-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
  background: var(--bg, #fff);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 44px;
  padding: 0 12px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--bd, #dcdfe6);
  background: var(--bg, #fff);
  position: relative;
  z-index: 50;
}

.header-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: var(--t2, #606266);
  flex-shrink: 0;
}

.header-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.header-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.header-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--t1, #303133);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.panel-messages {
  flex: 1;
  min-height: 0;
  max-height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  scrollbar-width: thin;
  display: block;
}

.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px 16px;
}

.welcome-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--t1, #303133);
  margin-bottom: 8px;
}

.welcome-sub {
  font-size: 14px;
  color: var(--t3, #909399);
}

.msg-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
  max-width: 680px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.msg-row.user { align-items: flex-end; }
.msg-row.assistant { align-items: flex-start; }

.panel-input {
  flex-shrink: 0;
  padding: 12px 16px 16px;
  background: var(--bg, #fff);
  display: flex;
  justify-content: center;
}

.input-wrapper {
  width: 100%;
  max-width: 680px;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: #fff;
  border: 1px solid var(--bd, #dcdfe6);
  border-radius: 16px;
  padding: 8px 8px 8px 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper.focused {
  border-color: var(--el-color-primary, #3370ff);
  box-shadow: 0 0 0 2px rgba(51, 112, 255, 0.1);
}

.input-wrapper textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  background: transparent;
  color: var(--t1, #303133);
  min-height: 24px;
  max-height: 160px;
  padding: 4px 0;
  word-break: break-word;
}

.input-wrapper textarea::placeholder {
  color: var(--t3, #909399);
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: var(--bd, #dcdfe6);
  color: var(--t3, #909399);
  cursor: not-allowed;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s, color 0.2s, transform 0.1s;
}

.send-btn.active {
  background: var(--t1, #303133);
  color: #fff;
  cursor: pointer;
}

.send-btn.active:hover { opacity: 0.85; }
.send-btn.active:active { transform: scale(0.92); }

.send-btn.stop {
  background: #ef4444;
  color: #fff;
  cursor: pointer;
}

.send-btn.stop:hover { background: #dc2626; }
.send-btn.stop:active { transform: scale(0.92); }
</style>
