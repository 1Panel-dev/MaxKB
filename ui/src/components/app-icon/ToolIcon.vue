<template>
  <el-avatar v-if="type == 'MCP'" shape="square" :size="size">
    <img src="@/assets/tool/icon_mcp.svg" style="width: 75%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="type == 'DATA_SOURCE'" class="avatar-purple" shape="square" :size="size">
    <img src="@/assets/tool/icon_datasource.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else class="avatar-green" shape="square" :size="size">
    <img src="@/assets/tool/icon_tool.svg" style="width: 58%" alt="" />
  </el-avatar>
</template>
<script setup lang="ts">
defineOptions({ name: 'ToolIcon' })
const props = defineProps({
  type: {
    type: [String, Number],
    default: '',
  },
  size: {
    type: [String, Number],
    default: 32,
  },
})
</script>
