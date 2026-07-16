<template>
  <div class="chat-panel">
    <!-- Header -->
    <div class="chat-panel__header">
      <slot name="header">
        <div class="default-header">
          <button v-if="showBack" class="header-btn" @click="$emit('back')">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="header-btn" @click="$emit('toggle')">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
          </button>
          <div class="header-info">
            <img v-if="icon" :src="icon" class="header-icon" />
            <span class="header-title">{{ title || '新对话' }}</span>
          </div>
        </div>
      </slot>
    </div>

    <!-- Messages -->
    <div ref="msgBoxRef" class="chat-panel__messages" @scroll="onScroll">
      <div class="chat-panel__content">
        <slot name="empty" v-if="messages.length === 0 && !loading">
          <div class="default-empty">
            <p class="empty-title">{{ title || 'AI 助手' }}</p>
            <p class="empty-sub">有什么可以帮你的？</p>
          </div>
        </slot>

        <template v-else>
          <div
            v-for="(msg, i) in messages"
            :key="msg.id || i"
            :class="['msg-row', msg.role]"
          >
            <slot name="message" :message="msg" :index="i">
              <div class="msg-content">{{ msg.content }}</div>
            </slot>
          </div>

          <div v-if="streamLoading" class="msg-row ASSISTANT">
            <slot name="loading">
              <div class="default-loading">
                <span></span><span></span><span></span>
              </div>
            </slot>
          </div>
        </template>
      </div>
    </div>

    <!-- Input -->
    <div class="chat-panel__input">
      <slot name="input">
        <div class="default-input">
          <textarea
            ref="inputRef"
            v-model="inputText"
            :disabled="streamLoading"
            :placeholder="streamLoading ? '正在回复中...' : '输入消息...'"
            @keydown="onKeydown"
            rows="1"
          />
          <button
            v-if="!streamLoading"
            class="send-btn"
            :class="{ active: canSend }"
            :disabled="!canSend"
            @click="send"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 14V2M3 7l5-5 5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button v-else class="send-btn stop" @click="$emit('stop')">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect x="2" y="2" width="10" height="10" rx="2" fill="currentColor"/>
            </svg>
          </button>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted } from 'vue'
import { Scroll } from '../../index'

const props = withDefaults(
  defineProps<{
    messages?: any[]
    loading?: boolean
    streamLoading?: boolean
    title?: string
    icon?: string
    showBack?: boolean
  }>(),
  {
    messages: () => [],
    loading: false,
    streamLoading: false,
    showBack: false,
  },
)

const emit = defineEmits<{
  send: [text: string]
  stop: []
  back: []
  toggle: []
  scroll: []
}>()

const inputText = ref('')
const inputRef = ref<HTMLTextAreaElement | null>(null)
const msgBoxRef = ref<HTMLElement | null>(null)

let scroll: InstanceType<typeof Scroll> | null = null

const canSend = computed(() => inputText.value.trim() && !props.streamLoading)

onMounted(() => {
  if (msgBoxRef.value) {
    scroll = new Scroll(msgBoxRef.value)
  }
})

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
    e.preventDefault()
    send()
  }
}

const send = () => {
  if (!canSend.value) return
  emit('send', inputText.value.trim())
  inputText.value = ''
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.style.height = 'auto'
    }
  })
}

const onScroll = () => {
  const el = msgBoxRef.value
  if (!el || el.scrollTop > 60) return
  emit('scroll')
}

const scrollToBottom = () => {
  scroll?.forceBottom()
}

watch(() => props.messages.length, () => {
  nextTick(() => scroll?.scrollBottom())
})

defineExpose({ scrollToBottom })
</script>
