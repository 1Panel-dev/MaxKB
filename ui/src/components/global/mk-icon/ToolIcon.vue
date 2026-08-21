<script setup lang="ts">
import { resetUrl } from '@/utils/common'
import { TOOL_TYPE } from '@/api/enums'
defineOptions({ name: 'ToolIcon' })
const props = defineProps({
  type: {
    type: [String, Number],
    default: '',
  },
  size: {
    type: [String, Number],
    default: 24,
  },
  icon: String,
})
</script>
<template>
  <el-avatar v-if="icon" shape="square" :size="size" style="background: none">
    <img :src="resetUrl(icon)" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == TOOL_TYPE.MCP" shape="square" :size="size">
    <img src="@/assets/tool/icon_mcp.svg" style="width: 73%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == TOOL_TYPE.SKILL" shape="square" :size="size">
    <img src="@/assets/tool/icon_skill.svg" style="width: 63%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == TOOL_TYPE.DATA_SOURCE" class="bg-purple!" shape="square" :size="size">
    <img src="@/assets/tool/icon_datasource.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == TOOL_TYPE.WORKFLOW" class="bg-success!" shape="square" :size="size">
    <img src="@/assets/workflow/logo_workflow.svg" style="width: 62%" alt="" />
  </el-avatar>
  <el-avatar v-else class="bg-success!" shape="square" :size="size">
    <img src="@/assets/tool/icon_tool.svg" style="width: 63%" alt="" />
  </el-avatar>
</template>
