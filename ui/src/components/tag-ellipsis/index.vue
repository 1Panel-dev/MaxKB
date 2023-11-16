<template>
  <el-tag class="tag-ellipsis flex-between mb-8" effect="plain" v-bind="$attrs">
    <el-tooltip
      :disabled="!isShowTooltip"
      effect="dark"
      :content="tooltipContent"
      placement="bottom"
    >
      <div ref="tagLabel">
        <slot></slot>
      </div>
    </el-tooltip>
  </el-tag>
</template>
<script setup lang="ts">
import { ref, computed, useSlots } from 'vue'
defineOptions({ name: 'TagEllipsis' })
const slots = useSlots()
const tooltipContent = slots.default()?.[0].children || ''
const tagLabel = ref()
const isShowTooltip = computed(() => {
  const containerWeight = tagLabel.value?.scrollWidth
  const contentWeight = tagLabel.value?.clientWidth
  if (containerWeight > contentWeight) {
    // 实际宽度 > 可视宽度
    return true
  } else {
    // 否则为不溢出
    return false
  }
})
</script>
<style lang="scss" scoped>
// tag超出省略号
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
  :deep(.el-tooltip__trigger) {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
}
</style>
