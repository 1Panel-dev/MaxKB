<template>
  <div class="main-layout h-full flex">
    <div class="sidebar-container"><Sidebar /></div>
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
  transition: width 0.28s;
  width: var(--sidebar-width);
  background-color: var(--sidebar-bg-color);
  border-right: 1px solid var(--el-border-color);
}
</style>
