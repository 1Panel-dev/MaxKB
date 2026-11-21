<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import HistoryPopover from './history-popover/index.vue'

const { t } = useI18n({ useScope: 'global' })
// 左栏放外部设置表单，开合沿用会话列表 store 的侧栏状态。
const { appInfo, leftSideOpen, toggleLeftSide, newConversation } = useConversationListStore()
</script>

<template>
  <header class="flex-align-center h-header shrink-0 gap-1 px-3">
    <MkTooltip :content="leftSideOpen ? t('chat.actions.collapseSettings') : t('chat.actions.expandSettings')">
      <!-- 收起或展开左侧设置表单 -->
      <el-button text @click="toggleLeftSide()">
        <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
      </el-button>
    </MkTooltip>
    <el-divider direction="vertical" class="ml-2! mr-3!" />
    <ApplicationIcon :icon="appInfo?.icon" :size="24" class="shrink-0" />
    <h4 class="ml-1 min-w-0 flex-1 truncate" :title="appInfo?.name">{{ appInfo?.name }}</h4>
    <MkTooltip :content="t('chat.newChat')">
      <!-- 新建对话 -->
      <el-button text @click="newConversation()">
        <MkIcon name="icon_new-chat_outlined" :size="18" />
      </el-button>
    </MkTooltip>
    <!-- 历史记录 -->
    <span class="ml-1">
      <HistoryPopover />
    </span>
  </header>
</template>
