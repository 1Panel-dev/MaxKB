<script setup lang="ts">
import type { ToolType } from '@/api/types'

const props = defineProps<{
  item?: {
    name: string
    icon: string
    tool_type: ToolType
    kind?: string
  }
  size?: string | number
}>()
</script>

<template>
  <ToolIcon v-if="item?.kind !== 'data-source'" :icon="props.item?.icon" :type="props.item?.tool_type" />
  <el-avatar v-else-if="item?.kind === 'data-source'" class="bg-purple!" shape="square">
    <img src="@/assets/tool/icon_datasource.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else class="bg-success!" shape="square" :size="size">
    <img style="width: 63%" src="@/assets/tool/icon_tool.svg" alt="" />
  </el-avatar>
</template>
