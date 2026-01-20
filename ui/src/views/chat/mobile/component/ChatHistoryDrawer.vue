<template>
  <div>
    <el-drawer
      v-model="show"
      :with-header="false"
      class="chat-history-drawer"
      direction="ltr"
      :size="280"
      style="--el-drawer-padding-primary: 0"
    >
      <HistoryPanel
        :application-detail="applicationDetail"
        :chat-log-data="chatLogData"
        :left-loading="leftLoading"
        :currentChatId="currentChatId"
        @new-chat="newChat"
        @clickLog="handleClickList"
        @delete-log="deleteChatLog"
        @refreshFieldTitle="refreshFieldTitle"
        @clear-chat="clearChat"
      >
        <div class="flex align-center user-info p-16" @click="toUserCenter">
          <el-avatar
            :size="32"
            :class="`${!chatUser.chat_profile?.authentication || chatUser.chat_profile.authentication_type === 'password' ? 'cursor-default' : ''}`"
          >
            <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
          </el-avatar>
          <span v-if="chatUser.chat_profile?.authentication" class="ml-8 color-text-primary">
            {{ chatUser.chatUserProfile?.nick_name }}
          </span>
        </div>
      </HistoryPanel>
    </el-drawer>

    <UserCenterDrawer v-model:show="userCenterDrawerShow" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import useStore from '@/stores'
import UserCenterDrawer from './UserCenterDrawer.vue'
import HistoryPanel from '@/views/chat/component/HistoryPanel.vue'

const show = defineModel<boolean>('show')

const props = defineProps<{
  applicationDetail: any
  chatLogData: any[]
  leftLoading?: boolean
  currentChatId: string
}>()

const emit = defineEmits(['newChat', 'clickLog', 'deleteLog', 'refreshFieldTitle', 'clearChat'])

const { chatUser } = useStore()

const clearChat = () => {
  emit('clearChat')
}

const newChat = () => {
  emit('newChat')
}

const handleClickList = (item: any) => {
  emit('clickLog', item)
}

const deleteChatLog = (row: any) => {
  emit('deleteLog', row)
}
function refreshFieldTitle(chatId: string, abstract: string) {
  emit('refreshFieldTitle', chatId, abstract)
}

const userCenterDrawerShow = ref(false)
function toUserCenter() {
  if (
    !chatUser.chat_profile?.authentication ||
    chatUser.chat_profile.authentication_type === 'password'
  )
    return
  userCenterDrawerShow.value = true
}
</script>

<style lang="scss" scoped>
:deep(.chat-history-drawer) {
  .el-drawer__body {
    padding: 0 !important;
  }
}
</style>
