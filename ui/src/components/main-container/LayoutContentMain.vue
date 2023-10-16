<template>
  <div class="content-container__main">
    <div class="content-container__toolbar" v-if="slots.toolbar">
      <slot name="toolbar"></slot>
    </div>
    <slot></slot>
  </div>
</template>

<script setup>
import { useSlots } from 'vue';
defineOptions({ name: 'LayoutContentMain' });
const slots = useSlots();
</script>

<style lang="scss">
@use '@/styles/common/mixins.scss' as *;
@use '@/styles/common/variables.scss' as *;

.content-container__main {
  background-color: #ffffff;
  padding: $view-padding;
  border-radius: 4px;
  box-sizing: border-box;
  min-height: calc(100vh - 210px);

  .content-container__toolbar {
    @include flex-row(space-between, center);
    margin-bottom: 10px;
  }
}
</style>
