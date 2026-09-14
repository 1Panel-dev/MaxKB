<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import type { KnowledgeItem } from '@/api/types'

defineOptions({ name: 'SettingKnowledgeAction' })

const props = defineProps<{ knowledge: KnowledgeItem; label: string }>()
const route = useRoute()
const router = useRouter()

function handleSettingKnowledge(event: MouseEvent) {
  event.stopPropagation()
  void router.push({
    name: 'workspace-knowledge-setting',
    params: { workspaceId: route.params.workspaceId, knowledgeId: props.knowledge.id },
  })
}
</script>

<template>
  <!-- 打开知识库设置 -->
  <MkDropdownItem @click="handleSettingKnowledge">
    <template #icon><MkIcon name="icon_setting" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
