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
  <header class="mk-conversation-chat-header flex-align-center p-4">
    <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
    <template v-if="!list.leftSideOpen.value">
      <!-- 展开左侧 -->
      <el-button text @click="list.toggleLeftSide()" class="-ml-1">
        <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
      </el-button>
    </template>

    <div class="flex-1 flex-align-center gap-2">
      <h4 class="truncate">{{ list.currentConversation.value?.abstract || '新建对话' }}</h4>
    </div>
    <!-- 新建对话 -->
    <el-button text @click="handleNewConversation">
      <MkIcon name="icon_new-chat_outlined" :size="18" class="text-N900!" />
    </el-button>
    <!-- 进入分享模式，勾选要分享的对话 -->
    <el-button v-if="shareable" text :disabled="!canShare" @click="emit('share')">
      <MkIcon name="icon_share_outlined" :size="18" :class="canShare ? 'text-N900!' : 'text-N400!'" />
    </el-button>
    <slot />
  </header>
</template>

<style scoped lang="scss"></style>
