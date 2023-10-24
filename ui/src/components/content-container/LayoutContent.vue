<template>
  <div class="content-container">
    <div class="content-container__header mb-10" v-if="slots.header || header">
      <slot name="header">
        <span>{{ header }}</span>
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
import { useSlots } from 'vue'
defineOptions({ name: 'LayoutContent' })
const slots = useSlots()
defineProps({
  header: String
})
</script>

<style lang="scss" scope>
.content-container {
  transition: 0.3s;

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
