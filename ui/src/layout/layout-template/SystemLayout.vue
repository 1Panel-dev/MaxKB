<template>
  <div class="app-layout">
    <AppHeader />
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
import { AppHeader, Sidebar, AppMain } from '../components'
</script>
<style lang="scss" scoped>
@import './index.scss';
</style>
