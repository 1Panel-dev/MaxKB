<template>
  <div class="conversation-plus" :class="{ 'sidebar-open': sidebarOpen }">
    <div class="conv-sidebar" :class="{ open: sidebarOpen }">
      <Sidebar
        :type="type"
        :mode="sidebarMode"
        :open="sidebarOpen"
        @update:open="sidebarOpen = $event"
        @update:mode="sidebarMode = $event"
      />
    </div>

    <div v-if="sidebarOpen && isMobile" class="conv-mask" @click="sidebarOpen = false" />

    <div class="conv-main">
      <ChatPanel
        ref="panelRef"
        :type="type"
        :app-info="store.appInfo.value"
        @toggle="sidebarOpen = !sidebarOpen"
        @refresh="(cid: string) => emit('refresh', cid)"
        @stop="store.stopWorkflow(store.currentChatId.value)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, provide } from 'vue'
import { useChatStoreByType } from './common/use-chat-store'
import type { ChatType } from './common/types'
import ChatPanel from './chat-panel/index.vue'
import Sidebar from './sidebar/index.vue'

type OpenMode = boolean | 'auto'
type LayoutMode = 'push' | 'drawer' | 'auto'

const props = withDefaults(
  defineProps<{
    type?: ChatType
    defaultOpen?: OpenMode
    defaultMode?: LayoutMode
  }>(),
  {
    type: 'CHAT',
    defaultOpen: 'auto',
    defaultMode: 'auto',
  },
)

const emit = defineEmits<{
  openChat: [chatId: string]
  refresh: [chatId: string]
}>()

const store = useChatStoreByType(props.type)
provide('chat', store)

const BREAKPOINT = 768
const isMobile = ref(window.innerWidth < BREAKPOINT)
const updateMobile = () => { isMobile.value = window.innerWidth < BREAKPOINT }
onMounted(() => window.addEventListener('resize', updateMobile))
onBeforeUnmount(() => window.removeEventListener('resize', updateMobile))

const sidebarMode = ref<'push' | 'drawer'>(
  props.defaultMode === 'auto'
    ? isMobile.value ? 'drawer' : 'push'
    : props.defaultMode
)

const sidebarOpen = ref(
  props.defaultOpen === 'auto' ? !isMobile.value : props.defaultOpen
)

const panelRef = ref()

if (props.defaultOpen === 'auto') {
  watch(isMobile, (mobile) => {
    sidebarOpen.value = !mobile
  })
}

if (props.defaultMode === 'auto') {
  watch(isMobile, (mobile) => {
    sidebarMode.value = mobile ? 'drawer' : 'push'
  })
}

const onResize = () => { isMobile.value = window.innerWidth < 768 }

onMounted(() => {
  window.addEventListener('resize', onResize)
  store.loadConversations()
  store.fetchAppInfo(store.applicationId.value)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  store.cancelWorkflow(store.currentChatId.value)
})
</script>

<style scoped lang="scss">
.conversation-plus {
  display: flex;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.conv-sidebar {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid var(--bd, #dcdfe6);
  overflow-y: auto;
  transition: width 0.25s ease, transform 0.25s ease;
}

.conv-sidebar:not(.open) {
  width: 0;
  overflow: hidden;
  border-right: none;
}

.conv-mask {
  display: none;
  position: absolute;
  inset: 0;
  z-index: 30;
  background: rgba(0, 0, 0, 0.4);
}

.conv-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

@media only screen and (max-width: 768px) {
  .conv-sidebar {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
  }

  .conv-sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 16px rgba(0, 0, 0, 0.2);
  }

  .conversation-plus.sidebar-open .conv-mask {
    display: block;
  }
}
</style>
