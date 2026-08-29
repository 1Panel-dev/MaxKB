<script setup lang="ts">
import { resetUrl } from '@/utils/common'
defineOptions({ name: 'KnowledgeIcon' })
withDefaults(
  defineProps<{
    icon?: string
    size?: number | string
    type?: KnowledgeType
  }>(),
  {
    size: 24,
  },
)
</script>
<template>
  <el-avatar v-if="icon" class="bg-transparent!" shape="square" :size="size">
    <img :src="resetUrl(icon)" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == 1" class="bg-purple" shape="square" :size="size">
    <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == 2" class="bg-transparent!" shape="square" :size="size">
    <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == 4" class="bg-purple" shape="square" :size="size">
    <img src="@/assets/workflow/logo_workflow.svg" style="width: 60%" alt="" />
  </el-avatar>
  <el-avatar v-else shape="square" :size="size">
    <img src="@/assets/knowledge/icon_knowledge.svg" style="width: 58%" alt="" />
  </el-avatar>
</template>
