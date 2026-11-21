<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import { DEVICE_TYPE, useDeviceType, useShowShare } from '../../../view/index'
import { useMessageListStore } from '../../message-list/index'
import ExportAction from '../header-actions/export/ExportAction.vue'
import HeaderActions from '../header-actions/index.vue'

const props = defineProps<{
  /** 新建对话；不传时在当前应用中新建（门户在没有当前智能体时改为选择智能体） */
  newConversation?: () => void
}>()

const emit = defineEmits<{ share: [] }>()

const { t } = useI18n({ useScope: 'global' })
const list = useConversationListStore()
const msgs = useMessageListStore()
// 回答生成中或没有消息时不可分享
const canShare = computed(() => msgs.messages.value.length > 0 && !msgs.streamLoading.value && !msgs.loading.value)
const showShare = useShowShare()
const deviceType = useDeviceType()

const handleNewConversation = () => (props.newConversation ? props.newConversation() : list.newConversation())
</script>

<template>
  <header class="flex-align-center gap-1 p-4">
    <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
    <template v-if="!list.leftSideOpen.value">
      <!-- 展开左侧 -->
      <MkTooltip :content="t('chat.actions.expandSidebar')">
        <el-button text @click="list.toggleLeftSide()" class="-ml-1 mr-2">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </template>

    <div class="flex-1 flex-align-center gap-2">
      <h4 class="truncate">{{ list.currentConversation.value?.abstract || t('chat.newChat') }}</h4>
      <el-tag type="info" class="max-md:hidden!">
        <div class="flex-align-center gap-1">
          <ApplicationIcon :icon="list.appInfo.value?.icon" :size="18" class="shrink-0" />
          <span v-if="list.appInfo.value?.name" :title="list.appInfo.value.name" class="truncate text-sm">{{ list.appInfo.value.name }}</span>
        </div>
      </el-tag>
    </div>

    <!-- 新建对话 -->

    <MkTooltip :content="t('chat.newChat')" v-if="!list.leftSideOpen.value">
      <el-button text @click="handleNewConversation" class="mr-1">
        <MkIcon name="icon_new-chat_outlined" :size="18" class="text-N900!" />
      </el-button>
    </MkTooltip>
    <HeaderActions :collapse="deviceType === DEVICE_TYPE.MOBILE">
      <!-- 进入分享模式，勾选要分享的对话 -->
      <MkAction v-if="showShare" :label="t('chat.share.label')" icon="icon_share_outlined" :size="18" :disabled="!canShare" @click="emit('share')" />
      <!-- 导出当前对话 -->
      <ExportAction />
      <slot />
    </HeaderActions>
  </header>
</template>

<style scoped lang="scss"></style>
