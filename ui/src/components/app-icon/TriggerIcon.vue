<template>
  <el-avatar v-if="type == 'EVENT'" class="avatar-orange" shape="square" :size="size">
    <img src="@/assets/trigger/icon_event.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar v-else shape="square" :size="size">
    <img src="@/assets/trigger/icon_scheduled.svg" style="width: 58%" alt="" />
  </el-avatar>
</template>
<script setup lang="ts">
defineOptions({ name: 'TriggerIcon' })
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
