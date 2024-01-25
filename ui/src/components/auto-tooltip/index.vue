<template>
  <el-tooltip
    v-bind="$attrs"
    :disabled="!(containerWeight > contentWeight)"
    effect="dark"
    placement="bottom"
  >
    <div ref="tagLabel" class="auto-tooltip">
      <slot></slot>
    </div>
  </el-tooltip>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
defineOptions({ name: 'AutoTooltip' })
const tagLabel = ref()
const containerWeight = ref(0)
const contentWeight = ref(0)

onMounted(() => {
  nextTick(() => {
    containerWeight.value = tagLabel.value?.scrollWidth
    contentWeight.value = tagLabel.value?.clientWidth
  })
  window.addEventListener('resize', function () {
    containerWeight.value = tagLabel.value?.scrollWidth
    contentWeight.value = tagLabel.value?.clientWidth
  })
})
</script>
<style lang="scss" scoped>
.auto-tooltip {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>
