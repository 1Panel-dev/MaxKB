<script setup lang="ts">
import type { TriggerType } from '@/api/types'

defineOptions({ name: 'TriggerIcon' })

withDefaults(defineProps<{ size?: number | string; type?: TriggerType | string }>(), { size: 24 })
</script>

<template>
  <el-avatar v-if="type == 'SCHEDULED'" shape="square" :size="size">
    <img src="@/assets/trigger/icon_scheduled.svg" style="width: 58%" alt="" />
  </el-avatar>

  <el-avatar v-else class="bg-warning!" shape="square" :size="size">
    <img src="@/assets/trigger/icon_event.svg" style="width: 58%" alt="" />
  </el-avatar>
</template>
