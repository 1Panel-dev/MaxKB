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
      <el-button class="collapse cursor" circle @click="show = !show">
        <el-icon>
          <component :is="!show ? 'ArrowRightBold' : 'ArrowLeftBold'" />
        </el-icon>
      </el-button>
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
              <span class="ml-8 color-text-primary">{{ chatUser.chatUserProfile?.nick_name }}</span>
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
                      {{ `${$t('common.username')}: ${chatUser.chatUserProfile?.username}` }}
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
    </el-drawer>

    <ResetPassword
      ref="resetPasswordRef"
      emitConfirm
      @confirm="handleResetPassword"
    ></ResetPassword>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineModel } from 'vue'
import useStore from '@/stores'
import HistoryPanel from '@/views/chat/component/HistoryPanel.vue'
import ResetPassword from '@/layout/layout-header/avatar/ResetPassword.vue'
import type { ResetCurrentUserPasswordRequest } from '@/api/type/user'
import chatAPI from '@/api/chat/chat'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()
const show = defineModel<boolean>('show')

const props = defineProps<{
  applicationDetail: any
  chatLogData: any[]
  leftLoading: boolean
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

const resetPasswordRef = ref<InstanceType<typeof ResetPassword>>()
const openResetPassword = () => {
  resetPasswordRef.value?.open()
}

const handleResetPassword = (param: ResetCurrentUserPasswordRequest) => {
  chatAPI.resetCurrentPassword(param).then(() => {
    router.push({ name: 'login' })
  })
}

const logout = () => {
  chatUser.logout().then(() => {
    router.push({
      name: 'login',
      params: { accessToken: chatUser.accessToken },
      query: route.query,
    })
  })
}
</script>

<style lang="scss" scoped>
:deep(.chat-history-drawer) {
  overflow: visible;

  .el-drawer__body {
    padding: 0 !important;

    .collapse {
      position: absolute;
      top: 20px;
      right: -13px;
      box-shadow: 0px 5px 10px 0px var(--app-text-color-light-1);
      z-index: 1;
      width: 24px;
      height: 24px;
    }
  }
}
</style>
