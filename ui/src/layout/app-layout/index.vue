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
<style lang="scss" scoped>
.app-layout {
  background-color: var(--app-layout-bg-color);
}

.app-main {
  height: calc(100vh - var(--app-header-height));
  padding: 0 !important;
  box-sizing: border-box;
}
.app-header {
  background: var(--app-header-bg-color);
}
</style>
