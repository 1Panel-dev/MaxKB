<template>
  <el-avatar
    v-if="isAppIcon(item?.icon)"
    shape="square"
    :size="32"
    style="background: none"
    class="mr-8"
  >
    <img :src="item?.icon" alt="" />
  </el-avatar>
  <el-avatar v-else-if="item?.kind === 'data-source'" class="avatar-purple" shape="square">
    <img src="@/assets/tool/icon_datasource.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else-if="item?.tool_type === 'DATA_SOURCE'" class="avatar-purple" shape="square">
    <img src="@/assets/tool/icon_datasource.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else shape="square" style="background: #34c724">
    <img src="@/assets/tool/icon_tool.svg" style="width: 75%" alt="" />
  </el-avatar>
</template>
<script setup lang="ts">
import { isAppIcon } from '@/utils/common'
const props = defineProps<{
  item?: {
    name: string
    icon: string
    tool_type: string
    kind?: string
  }
}>()
</script>

<script setup lang="ts"></script>
