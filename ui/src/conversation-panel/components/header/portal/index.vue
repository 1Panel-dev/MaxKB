<script setup lang="ts">
import { computed } from 'vue'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import { useMessageListStore } from '../../message-list/index'

const props = defineProps<{
  /** 新建对话；不传时在当前应用中新建（门户在没有当前智能体时改为选择智能体） */
  newConversation?: () => void
  /** 显示分享入口；仅对话端传入 */
  shareable?: boolean
}>()

const emit = defineEmits<{ share: [] }>()

const list = useConversationListStore()
const msgs = useMessageListStore()
// 回答生成中或没有消息时不可分享
const canShare = computed(() => msgs.messages.value.length > 0 && !msgs.streamLoading.value)

const handleNewConversation = () => (props.newConversation ? props.newConversation() : list.newConversation())
</script>

<template>
  <header class="flex-align-center py-4 px-6">
    <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
    <template v-if="!list.leftSideOpen.value">
      <!-- 展开左侧 -->
      <MkTooltip content="展开侧边栏">
        <el-button text @click="list.toggleLeftSide()">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>

      <!-- 新建对话 -->
      <MkTooltip content="新建对话">
        <el-button text @click="handleNewConversation">
          <MkIcon name="icon_new-chat_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
      <el-divider direction="vertical" class="ml-3! mr-4!" />
    </template>

    <div class="flex-1 flex-align-center">
      <h4 class="truncate">{{ list.currentConversation.value?.abstract || '新建对话' }}</h4>
      <el-tag type="info">
        <div class="flex-align-center gap-1">
          <ApplicationIcon :icon="list.appInfo.value?.icon" :size="18" class="shrink-0" />
          <span v-if="list.appInfo.value?.name" class="text-sm">{{ list.appInfo.value.name }}</span>
        </div>
      </el-tag>
    </div>
    <!-- 进入分享模式，勾选要分享的对话 -->
    <MkTooltip v-if="shareable" content="分享">
      <el-button text :disabled="!canShare" @click="emit('share')">
        <MkIcon name="icon_share_outlined" :size="18" class="text-N900!" />
      </el-button>
    </MkTooltip>
    <slot />
  </header>
</template>

<style scoped lang="scss"></style>
