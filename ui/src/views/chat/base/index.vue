<template>
  <div class="chat layout-bg" v-loading="loading">
    <div class="chat__header" :class="!isDefaultTheme ? 'custom-header' : ''">
      <div class="chat-width flex align-center">
        <div class="mr-12 ml-24 flex">
          <AppAvatar
            v-if="isAppIcon(applicationDetail?.icon)"
            shape="square"
            :size="32"
            style="background: none"
          >
            <img :src="applicationDetail?.icon" alt="" />
          </AppAvatar>
          <AppAvatar
            v-else-if="applicationDetail?.name"
            :name="applicationDetail?.name"
            pinyinColor
            shape="square"
            :size="32"
          />
        </div>

        <h2>{{ applicationDetail?.name }}</h2>
      </div>
    </div>
    <div class="chat__main chat-width">
      <AiChat
        v-model:applicationDetails="applicationDetail"
        type="ai-chat"
        :available="applicationAvailable"
        :appId="applicationDetail?.id"
        :record="recordList"
        :chatId="currentChatId"
        @refresh="refresh"
      >
        <template #operateBefore>
          <div>
            <el-button type="primary" link class="new-chat-button mb-8" @click="newChat">
              <el-icon><Plus /></el-icon><span class="ml-4">{{ $t('chat.createChat') }}</span>
            </el-button>
          </div>
        </template>
      </AiChat>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'

import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'

const { user } = useStore()

const isDefaultTheme = computed(() => {
  return user.isDefaultTheme()
})

const loading = ref(false)
const props = defineProps<{
  application_profile: any
  applicationAvailable: boolean
}>()
const applicationDetail = computed({
  get: () => {
    return props.application_profile
  },
  set: (v) => {}
})
const recordList = ref([])
const currentChatId = ref('')

function newChat() {
  currentChatId.value = 'new'
  recordList.value = []
}
function refresh(id: string) {
  currentChatId.value = id
}
</script>
<style lang="scss">
.chat {
  overflow: hidden;
  &__header {
    background: var(--app-header-bg-color);
    position: fixed;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 100;
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-border-color);
  }
  &__main {
    padding-top: calc(var(--app-header-height) + 24px);
    height: calc(100vh - var(--app-header-height) - 24px);
    overflow: hidden;
  }

  .chat-width {
    // max-width: 80%;
    margin: 0 auto;
  }
}
</style>
