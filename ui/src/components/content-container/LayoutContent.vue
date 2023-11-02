<template>
  <div class="content-container">
    <div class="content-container__header mt-16 mb-16" v-if="slots.header || header">
      <slot name="header">
        <back-button :to="backTo" v-if="showBack"></back-button>
        <h2 class="vertical-middle">{{ header }}</h2>
      </slot>
    </div>
    <el-scrollbar>
      <div class="content-container__main main-calc-height">
        <slot></slot>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'
defineOptions({ name: 'LayoutContent' })
const slots = useSlots()
const props = defineProps({
  header: String,
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
  }
  .content-container__main {
    background-color: var(--app-view-bg-color);
    border-radius: 4px;
    box-sizing: border-box;
  }
}
</style>
