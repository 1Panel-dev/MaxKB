<template>
  <el-avatar :size="30" v-bind="$attrs">
    <slot> {{ firstUserName }} </slot>
  </el-avatar>
</template>
<script setup lang="ts">
import { computed } from 'vue'
defineOptions({ name: 'AppAvatar' })
const props = defineProps({
  name: {
    type: String,
    default: ''
  }
})

const firstUserName = computed(() => {
  return props.name?.substring(0, 1)
})
</script>
<style lang="scss" scoped></style>
