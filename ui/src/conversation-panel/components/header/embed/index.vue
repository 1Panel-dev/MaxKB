<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import { useShowShare } from '../../../view/index'
import { useMessageListStore } from '../../message-list/index'
import { useShareLinkStoreOptional } from '../../message-list/share/index'
import ExportAction from '../header-actions/export/ExportAction.vue'
import HeaderActions from '../header-actions/index.vue'

const { t } = useI18n({ useScope: 'global' })
const { appInfo, leftSideOpen, toggleLeftSide, newConversation } = useConversationListStore()
const showShare = useShowShare()
const msgs = useMessageListStore()
// 回答生成中或没有消息时不可分享
const canShare = computed(() => msgs.messages.value.length > 0 && !msgs.streamLoading.value)
const shareLink = useShareLinkStoreOptional()
</script>

<template>
  <header class="mk-conversation-embed-header flex-align-center h-header shrink-0 border-b px-3">
    <!-- 左侧收起时才在顶部显示展开按钮 -->
    <template v-if="!leftSideOpen">
      <MkTooltip :content="t('chat.actions.expandSidebar')">
        <!-- 展开左侧 -->
        <el-button text @click="toggleLeftSide()" class="mr-2">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </template>
    <ApplicationIcon :icon="appInfo?.icon" :size="24" class="shrink-0 mr-2" />
    <h4 class="min-w-0 flex-1 truncate font-semibold" :title="appInfo?.name">
      {{ appInfo?.name }}
    </h4>

    <MkTooltip :content="t('chat.newChat')">
      <!-- 新建对话 -->
      <el-button text @click="newConversation()">
        <MkIcon name="icon_new-chat_outlined" :size="18" />
      </el-button>
    </MkTooltip>
    <!-- 操作始终收进更多菜单 -->
    <HeaderActions always-collapse>
      <!-- 进入分享模式，勾选要分享的对话 -->
      <MkAction
        v-if="showShare"
        :label="t('chat.share.label')"
        :size="18"
        icon="icon_share_outlined"
        :disabled="!canShare"
        @click="shareLink?.enterShare()"
      />
      <!-- 导出对话 -->
      <ExportAction />
      <slot />
    </HeaderActions>
    <!-- 占位：嵌入脚本在 iframe 外层右上角叠加放大/还原与关闭按钮，保留与调试头部一致的两个按钮位置 -->
    <el-button text tabindex="-1" class="invisible pointer-events-none">
      <MkIcon name="icon_magnify_outlined" :size="18" />
    </el-button>
    <el-button text tabindex="-1" class="invisible pointer-events-none">
      <MkIcon name="icon_close_outlined" :size="18" />
    </el-button>
  </header>
</template>
