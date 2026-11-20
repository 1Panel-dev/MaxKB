<script setup lang="ts">
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'

const { appInfo, leftSideOpen, toggleLeftSide, newConversation } = useConversationListStore()
</script>

<template>
  <header class="mk-conversation-embed-header flex-align-center h-header shrink-0 border-b px-3">
    <!-- 左侧收起时才在顶部显示展开按钮 -->
    <template v-if="!leftSideOpen">
      <MkTooltip content="展开侧边栏">
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

    <MkTooltip content="新建对话">
      <!-- 新建对话 -->
      <el-button text @click="newConversation()">
        <MkIcon name="icon_new-chat_outlined" :size="18" />
      </el-button>
    </MkTooltip>
    <!-- 占位：嵌入脚本在 iframe 外层右上角叠加放大/还原与关闭按钮，保留与调试头部一致的两个按钮位置 -->
    <el-button text tabindex="-1" class="invisible pointer-events-none">
      <MkIcon name="icon_magnify_outlined" :size="18" />
    </el-button>
    <el-button text tabindex="-1" class="invisible pointer-events-none">
      <MkIcon name="icon_close_outlined" :size="18" />
    </el-button>
  </header>
</template>
