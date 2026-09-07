<script setup lang="ts">
import { computed } from 'vue'
import type { KnowledgeType } from '@/api/types'
import { KNOWLEDGE_TYPE_KEY, KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'

defineOptions({ name: 'KnowledgeIcon' })

const props = withDefaults(defineProps<{ size?: number | string; type?: KnowledgeType }>(), { size: 24 })
const knowledgeType = computed(() => (props.type === undefined ? undefined : KNOWLEDGE_TYPE_MAP[props.type]))
</script>
<template>
  <el-avatar v-if="knowledgeType === KNOWLEDGE_TYPE_KEY.WEB" class="bg-purple!" shape="square" :size="size">
    <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="knowledgeType === KNOWLEDGE_TYPE_KEY.LARK" class="bg-transparent!" shape="square" :size="size">
    <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="knowledgeType === KNOWLEDGE_TYPE_KEY.WORKFLOW" class="bg-purple!" shape="square" :size="size">
    <img src="@/assets/workflow/logo_workflow.svg" style="width: 60%" alt="" />
  </el-avatar>
  <el-avatar v-else shape="square" :size="size">
    <img src="@/assets/knowledge/icon_knowledge.svg" style="width: 58%" alt="" />
  </el-avatar>
</template>
