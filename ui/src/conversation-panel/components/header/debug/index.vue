<script setup lang="ts">
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import { useDebugHeaderStore } from './index'

const { appInfo, leftSideOpen, toggleLeftSide, newConversation } = useConversationListStore()
const debug = useDebugHeaderStore()
</script>

<template>
  <header class="mk-conversation-header flex-align-center h-header shrink-0 border-b px-3">
    <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话 -->
    <template v-if="!leftSideOpen">
      <MkTooltip content="展开侧边栏">
        <!-- 展开左侧 -->
        <el-button text @click="toggleLeftSide()" class="mr-2">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </template>
    <ApplicationIcon :icon="appInfo?.icon" :size="24" class="shrink-0 mr-2" />
    <!-- // TODO 没拿到appInfo -->
    <h4 class="min-w-0 flex-1 truncate font-semibold" :title="appInfo?.name">
      {{ appInfo?.name }}
    </h4>

    <MkTooltip content="新建对话">
      <!-- 新建对话 -->
      <el-button text @click="newConversation()">
        <MkIcon name="icon_new-chat_outlined" :size="18" />
      </el-button>
    </MkTooltip>
    <MkTooltip :content="debug.expanded.value ? '还原' : '放大'">
      <!-- 放大或还原调试面板 -->
      <el-button text @click="debug.toggleExpand()">
        <MkIcon :name="debug.expanded.value ? 'icon_minify_outlined' : 'icon_magnify_outlined'" :size="18" />
      </el-button>
    </MkTooltip>
    <MkTooltip content="关闭调试">
      <!-- 关闭调试 -->
      <el-button text @click="debug.close()">
        <MkIcon name="icon_close_outlined" :size="18" />
      </el-button>
    </MkTooltip>
  </header>
</template>

<style scoped lang="scss"></style>
