<template>
  <el-tag class="tag-ellipsis flex-between mb-8" effect="plain" v-bind="$attrs">
    <auto-tooltip :content="tooltipContent">
      <slot></slot>
    </auto-tooltip>
  </el-tag>
</template>
<script setup lang="ts">
import { ref, computed, useSlots } from 'vue'
defineOptions({ name: 'TagEllipsis' })
const slots = useSlots()
const tooltipContent = slots.default?.()?.[0].children || ''
</script>
<style lang="scss" scoped>
/* tag超出省略号 */
.tag-ellipsis {
  border: 1px solid var(--el-border-color);
  color: var(--app-text-color);
  border-radius: 4px;
  height: 30px;
  line-height: 30px;
  padding: 0 9px;
  box-sizing: border-box;

  :deep(.el-tag__content) {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  // :deep(.el-tooltip__trigger) {
  //   overflow: hidden;
  //   white-space: nowrap;
  //   text-overflow: ellipsis;
  // }
}
</style>
