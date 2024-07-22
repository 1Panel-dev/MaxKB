<template>
  <div class="content-container border-r-4">
    <div class="content-container__header flex align-center w-full" v-if="slots.header || header">
      <slot name="backButton">
        <back-button :to="backTo" v-if="showBack"></back-button>
      </slot>
      <slot name="header">
        <h4>{{ header }}</h4>
      </slot>
    </div>
    <el-scrollbar>
      <div class="content-container__main">
        <slot></slot>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'
defineOptions({ name: 'LayoutContainer' })
const slots = useSlots()
const props = defineProps({
  header: String || null,
  backTo: String
})
const showBack = computed(() => {
  const { backTo } = props
  return backTo
})
</script>

<style lang="scss" scope>
.content-container {
  transition: 0.3s;
  padding: 0 var(--app-view-padding) var(--app-view-padding);
  .content-container__header {
    box-sizing: border-box;
    padding: 16px 0;
    flex-wrap: wrap;
  }
  .content-container__main {
    background-color: var(--app-view-bg-color);
    box-sizing: border-box;
    min-width: 847px;
  }
}
</style>
