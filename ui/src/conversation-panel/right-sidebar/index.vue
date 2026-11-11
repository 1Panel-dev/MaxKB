<script setup lang="ts">
import ExecutionDetail from './execution-detail/index.vue'
import KnowledgeSource from './knowledge-source/index.vue'
import { RIGHT_SIDEBAR_PANEL, useRightSidebarStore } from './index'

defineOptions({ name: 'RightSidebar' })

const { panel } = useRightSidebarStore()
</script>

<template>
  <!-- 右侧栏：按当前面板展示执行详情或知识来源 -->
  <KnowledgeSource v-if="panel === RIGHT_SIDEBAR_PANEL.KNOWLEDGE_SOURCE" />
  <ExecutionDetail v-else />
</template>
