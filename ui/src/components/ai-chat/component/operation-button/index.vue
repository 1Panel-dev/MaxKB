<template>

  <div class="operation-button-container">

    <LogOperationButton
      v-if="type === 'log'"
      v-bind:data="chatRecord"
      @update:data="(event: any) => emit('update:chatRecord', event)"
      :applicationId="application.id"
      :tts="application.tts_model_enable"
      :tts_type="application.tts_type"
      :type="type"
    />

    <div class="mt-8" v-else>
      <el-button
        type="primary"
        v-if="chatRecord.is_stop && !chatRecord.write_ed"
        @click="startChat(chatRecord)"
        link
        >{{ $t('chat.operation.continue') }}
      </el-button>
      <el-button type="primary" v-else-if="!chatRecord.write_ed" @click="stopChat(chatRecord)" link
        >{{ $t('chat.operation.stopChat') }}
      </el-button>
    </div>

    <ChatOperationButton
      v-show="chatRecord.write_ed && 500 != chatRecord.status"
      :tts="application.tts_model_enable"
      :tts_type="application.tts_type"
      :tts_autoplay="application.tts_autoplay"
      :data="chatRecord"
      :type="type"
      :applicationId="application.id"
      :chatId="chatRecord.chat_id"
      :chat_loading="loading"
      @regeneration="regenerationChart(chatRecord)"
    />
  </div>
</template>
<script setup lang="ts">
import ChatOperationButton from '@/components/ai-chat/component/operation-button/ChatOperationButton.vue'
import LogOperationButton from '@/components/ai-chat/component/operation-button/LogOperationButton.vue'
import { type chatType } from '@/api/type/application'
defineProps<{
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
  chatRecord: chatType
  application: any
  loading: boolean
  startChat: (chat_record: any) => void
  stopChat: (chat_record: any) => void
  regenerationChart: (chat_record: any) => void
}>()
const emit = defineEmits(['update:chatRecord'])
</script>
<style lang="scss" scoped></style>
