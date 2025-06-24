<template>
  <div class="content-container">
    <div class="content-container__header flex align-center w-full" v-if="slots.header || header">
      <slot name="backButton">
        <back-button :to="backTo" v-if="showBack"></back-button>
      </slot>
      <div class="flex-between w-full">
        <slot name="header">
          <h4>{{ header }}</h4>
        </slot>
        <slot name="search"> </slot>
      </div>
    </div>

    <div class="content-container__main">
      <el-scrollbar class="p-16" style="padding-right: 0;">
        <slot></slot>
      </el-scrollbar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'
defineOptions({ name: 'ContentContainer' })
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
.content-container {
  transition: 0.3s;
  .content-container__header {
    box-sizing: border-box;
    padding: calc(var(--app-base-px) * 2) calc(var(--app-base-px) * 2) 0;
    flex-wrap: wrap;
  }
  .content-container__main {
    box-sizing: border-box;
    min-width: 447px;
  }
}
</style>
