<script setup lang="ts">
import { computed, onMounted, provide, ref } from 'vue'
import { useRoute } from 'vue-router'
import ConversationApi from '@/api/chat/conversation'
import type { ChatShareDetail } from '@/api/types'
import type { ChatMessage } from '@/conversation-panel/core/types'
import { SHARE_PANEL_CONTENT_KEY } from '@/conversation-panel/main/share-panel/index'
import SharePanel from '@/conversation-panel/main/share-panel/index.vue'

defineOptions({ name: 'ChatShare' })

const route = useRoute()
const shareId = computed(() => String(route.params.shareId || ''))
const detail = ref<ChatShareDetail | null>(null)
const loading = ref(false)

// 公开接口按时间正序返回全部记录，不请求原会话或加载更多历史。
const messages = computed<ChatMessage[]>(() =>
  (detail.value?.chat_record_list ?? []).flatMap((record) => {
    const attachments = record.execution_details?.find((entry) => entry.type === 'start-node') ?? {}
    const answers = (record.answer_text_list ?? []).flat()
    return [
      { id: `${record.id}_USER`, role: 'USER', content: [{ ...attachments, type: 'QUESTION', content: record.problem_text }] },
      {
        id: `${record.id}_ASSISTANT`,
        role: 'ASSISTANT',
        content: answers.length ? answers : [{ type: 'TEXT', content: record.answer_text }],
      },
    ]
  }),
)

provide(SHARE_PANEL_CONTENT_KEY, {
  title: computed(() => detail.value?.abstract || '分享对话'),
  appInfo: ref(null),
  messages,
  loading,
  hasMore: ref(false),
  loadMore: async () => false,
})

const loadShare = async () => {
  detail.value = null
  loading.value = true
  await ConversationApi.getShareConversation(shareId.value)
}
onMounted(loadShare)
</script>

<template>
  <main class="h-screen bg-white">
    <SharePanel />
  </main>
</template>

<style lang="scss"></style>
