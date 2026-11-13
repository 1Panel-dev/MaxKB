<script setup lang="ts">
import { computed } from 'vue'
import HeaderActions from '../header-actions/index.vue'
import ExportAction from '../header-actions/export/ExportAction.vue'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import { useMessageListStore } from '../../message-list/index'
import { useShareLinkStoreOptional } from '../../message-list/share/index'
import { DEVICE_TYPE, useDeviceType, useShowShare } from '../../../view/index'

const props = defineProps<{
  /** 新建对话；不传时在当前应用中新建（门户在没有当前智能体时改为选择智能体） */
  newConversation?: () => void
}>()
const list = useConversationListStore()

const msgs = useMessageListStore()
// 标题栏分享默认全选当前可分享记录
const shareLink = useShareLinkStoreOptional()
// 回答生成中或没有消息时不可分享
const canShare = computed(() => msgs.messages.value.length > 0 && !msgs.streamLoading.value)
const showShare = useShowShare()
const deviceType = useDeviceType()
const handleNewConversation = () => (props.newConversation ? props.newConversation() : list.newConversation())
</script>

<template>
  <header class="mk-conversation-chat-header flex-align-center gap-1 p-4">
    <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
    <template v-if="!list.leftSideOpen.value">
      <!-- 展开左侧 -->
      <MkTooltip content="展开侧边栏">
        <el-button text @click="list.toggleLeftSide()" class="-ml-1 mr-2">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </template>

    <div class="min-w-0 flex-1">
      <h4 class="truncate">{{ list.currentConversation.value?.abstract || '新建对话' }}</h4>
    </div>
    <template v-if="!list.isShared.value">
      <!-- 新建对话 -->
      <MkAction
        v-if="!list.leftSideOpen.value"
        display="button"
        label="新建对话"
        icon="icon_new-chat_outlined"
        class="text-N900!"
        @click="handleNewConversation"
      />
      <HeaderActions :collapse="deviceType === DEVICE_TYPE.MOBILE">
        <!-- 进入分享模式，勾选要分享的对话 -->
        <MkAction v-if="showShare" label="分享" icon="icon_share_outlined" :disabled="!canShare" @click="shareLink?.enterShare()" />
        <!-- 导出对话 -->
        <ExportAction />
        <slot />
      </HeaderActions>
    </template>
  </header>
</template>
