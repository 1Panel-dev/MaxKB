<script setup lang="ts">
import { computed } from 'vue'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import { useMessageListStore } from '../../message-list/index'
import { useShowShare } from '../../../view/index'

const props = defineProps<{
  /** 新建对话；不传时在当前应用中新建（门户在没有当前智能体时改为选择智能体） */
  newConversation?: () => void
}>()

const emit = defineEmits<{ share: [] }>()

const list = useConversationListStore()
const msgs = useMessageListStore()
// 回答生成中或没有消息时不可分享
const canShare = computed(() => msgs.messages.value.length > 0 && !msgs.streamLoading.value && !msgs.loading.value)
const showShare = useShowShare()

const handleNewConversation = () => (props.newConversation ? props.newConversation() : list.newConversation())
</script>

<template>
  <header class="flex-align-center gap-1 p-4">
    <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
    <template v-if="!list.leftSideOpen.value">
      <!-- 展开左侧 -->
      <MkTooltip content="展开侧边栏">
        <el-button text @click="list.toggleLeftSide()" class="-ml-1 mr-2">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </template>

    <div class="flex-1 flex-align-center gap-2">
      <h4 class="truncate">{{ list.currentConversation.value?.abstract || '新建对话' }}</h4>
      <el-tag type="info" class="max-md:hidden!">
        <div class="flex-align-center gap-1">
          <ApplicationIcon :icon="list.appInfo.value?.icon" :size="18" class="shrink-0" />
          <span v-if="list.appInfo.value?.name" :title="list.appInfo.value.name" class="truncate text-sm">{{ list.appInfo.value.name }}</span>
        </div>
      </el-tag>
    </div>
    <!-- 新建对话 -->
    <MkTooltip content="新建对话" v-if="!list.leftSideOpen.value">
      <el-button text @click="handleNewConversation">
        <MkIcon name="icon_new-chat_outlined" :size="18" class="text-N900!" />
      </el-button>
    </MkTooltip>
    <!-- 进入分享模式，勾选要分享的对话 -->
    <MkTooltip v-if="showShare" content="分享">
      <el-button text :disabled="!canShare" @click="emit('share')">
        <MkIcon name="icon_share_outlined" :size="18" :class="canShare ? 'text-N900!' : 'text-N400!'" />
      </el-button>
    </MkTooltip>
    <!-- 导出-->
    <MkTooltip content="导出">
      <el-button text>
        <MkIcon name="icon_export_outlined" :size="18" class="text-N900!" />
      </el-button>
    </MkTooltip>
    <slot />
  </header>
</template>

<style scoped lang="scss"></style>
