<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ShareConversation from '@/conversation-panel/view/share/index.vue'

defineOptions({ name: 'ChatShare' })

const route = useRoute()
const shareId = computed(() => String(route.params.shareId || ''))
</script>

<template>
  <main class="h-screen bg-white">
    <ShareConversation :share-id="shareId" />
  </main>
</template>
