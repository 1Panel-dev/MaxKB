<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ name: 'LoadingIcon' })

const props = withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })

const loadingSize = computed(() => (typeof props.size === 'number' ? `${props.size}px` : props.size))
</script>

<template>
  <div
    v-loading="true"
    class="loading-icon"
    :style="{
      '--el-loading-spinner-size': loadingSize,
      height: loadingSize,
      width: loadingSize,
    }"
    element-loading-background="transparent"
  ></div>
</template>
<style scoped lang="scss">
.loading-icon {
  :deep(.el-loading-spinner .path) {
    stroke-width: 4px;
  }
}
</style>
