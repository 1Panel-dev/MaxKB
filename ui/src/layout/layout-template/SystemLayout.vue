<template>
  <div class="app-layout">
    <div class="app-header">
      <TopBar />
    </div>
    <div class="app-main">
      <div class="main-layout h-full flex">
        <div class="sidebar-container">
          <Sidebar />
        </div>
        <div class="view-container">
          <AppMain />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TopBar, Sidebar, AppMain } from '../components'
</script>
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
.sidebar-container {
  box-sizing: border-box;
  transition: width 0.28s;
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background-color: var(--sidebar-bg-color);
}
.view-container {
  width: calc(100% - var(--sidebar-width));
}
</style>
