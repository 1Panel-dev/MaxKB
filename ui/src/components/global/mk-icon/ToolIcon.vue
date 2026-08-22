<script setup lang="ts">
import { TOOL_TYPE } from '@/api/enums'
import type { ToolType } from '@/api/types'
import { resetUrl } from '@/utils/common'

defineOptions({ name: 'ToolIcon' })

withDefaults(
  defineProps<{
    icon?: string
    size?: number | string
    type?: ToolType
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
  <el-avatar v-else-if="type === TOOL_TYPE.MCP" shape="square" :size="size">
    <img style="width: 73%" src="@/assets/tool/icon_mcp.svg" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type === TOOL_TYPE.SKILL" shape="square" :size="size">
    <img style="width: 60%" src="@/assets/tool/icon_skill.svg" alt="" />
  </el-avatar>
  <el-avatar
    v-else-if="type === TOOL_TYPE.DATA_SOURCE"
    class="bg-purple!"
    shape="square"
    :size="size"
  >
    <img style="width: 58%" src="@/assets/tool/icon_datasource.svg" alt="" />
  </el-avatar>
  <el-avatar
    v-else-if="type === TOOL_TYPE.WORKFLOW"
    class="bg-success!"
    shape="square"
    :size="size"
  >
    <img style="width: 62%" src="@/assets/workflow/logo_workflow.svg" alt="" />
  </el-avatar>
  <el-avatar v-else class="bg-success!" shape="square" :size="size">
    <img style="width: 63%" src="@/assets/tool/icon_tool.svg" alt="" />
  </el-avatar>
</template>
