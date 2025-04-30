<template>
  <div class="layout-container flex h-full">
    <div class="layout-container__left">
      <slot name="left"></slot>
    </div>
    <div class="layout-container__right">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'
defineOptions({ name: 'LayoutContainer' })
const slots = useSlots()
const props = defineProps({
  header: String || null,
  backTo: String,
})
const showBack = computed(() => {
  const { backTo } = props
  return backTo
})
</script>

<style lang="scss" scoped>
.layout-container {
  &__left {
    box-sizing: border-box;
    transition: width 0.28s;
    width: var(--sidebar-width);
    min-width: var(--sidebar-width);
    background-color: var(--sidebar-bg-color);
  }
  &__right {
    width: calc(100% - var(--sidebar-width));
  }
}
</style>
