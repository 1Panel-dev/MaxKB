<script setup lang="ts">
import { TopBar, AppMain } from '../components'
</script>

<template>
  <div class="app-layout">
    <div class="app-header">
      <TopBar />
    </div>
    <div class="app-main">
      <AppMain />
    </div>
  </div>
</template>
<style lang="scss">
.app-layout {
  background-color: var(--app-layout-bg-color);
  height: 100%;
}

.app-main {
  position: relative;
  height: 100%;
  padding: var(--app-header-height) 0 0 !important;
  box-sizing: border-box;
  overflow: auto;
}
.app-header {
  background: var(--app-header-bg-color);
  position: fixed;
  width: 100%;
  left: 0;
  top: 0;
  z-index: 100;
}
</style>
