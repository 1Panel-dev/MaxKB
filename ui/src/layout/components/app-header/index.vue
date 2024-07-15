<template>
  <div class="app-header">
    <TopBar>
      <template #logo> </template>
    </TopBar>
  </div>
</template>

<script setup lang="ts">
import TopBar from '../top-bar/index.vue'
import useStore from '@/stores'
const { common } = useStore()
</script>

<style lang="scss" scoped>
.app-header {
  background: var(--app-header-bg-color);
  position: fixed;
  width: 100%;
  left: 0;
  top: 0;
  z-index: 100;
}
</style>
