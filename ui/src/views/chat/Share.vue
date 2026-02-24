<template>
  <div class="chat-share">
    <div class="chat-width">
      <div class="p-16-24 flex-between">
        <h4 class="ellipsis-1" style="width: 66%">
          {{ currentChatName }}
        </h4>
      </div>
      <div class="chat-share__main">
        <AiChat ref="AiChatRef" :record="currentRecordList" type="share"> </AiChat>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { t } from '@/locales'
import chatAPI from '@/api/chat/chat'

const route = useRoute()
const {
  params: { link },
} = route as any

const currentChatName = ref(t('chat.createChat'))
const currentRecordList = ref<any>([])

function getShareChat() {
  chatAPI.getShareLink(link).then((res) => {
    if (res.data) {
      currentChatName.value = res.data.abstract
      currentRecordList.value = res.data.chat_record_list
    }
  })
}
onBeforeMount(() => {
  getShareChat()
})
</script>
<style lang="scss" scoped>
.chat-share {
  background: #eef1f4;
  &__main {
    height: calc(100vh - 60px);
  }
}
</style>
