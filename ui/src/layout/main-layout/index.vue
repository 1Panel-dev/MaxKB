<template>
  <div class="main-layout h-full flex">
    <div class="sidebar-container border-r"><Sidebar /></div>
    <div class="view-container">
      <AppMain />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sidebar, AppMain } from '../components'
</script>
<style lang="scss">
.sidebar-container {
  box-sizing: border-box;
  transition: width 0.28s;
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background-color: var(--sidebar-bg-color);
}
.view-container {
  width: 100%;
  padding: var(--app-view-padding);
}
</style>
