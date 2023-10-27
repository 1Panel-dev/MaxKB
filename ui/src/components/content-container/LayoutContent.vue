<template>
  <div class="content-container">
    <div class="content-container__header mb-10" v-if="slots.header || header">
      <slot name="header">
        <back-button :to="backTo" v-if="showBack"></back-button>
        <span class="vertical-middle">{{ header }}</span>
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
  padding: var(--app-view-padding);
  .content-container__header {
    font-weight: 600;
    font-size: 18px;
    box-sizing: border-box;
  }
  .content-container__main {
    background-color: var(--app-view-bg-color);
    border-radius: 6px;
    box-sizing: border-box;
    // overflow: auto;
    // height: 100%;
  }
}
</style>
