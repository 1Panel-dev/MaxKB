<template>
  <div class="main-layout h-full flex">
    <div class="sidebar-container">
      <Sidebar />
    </div>
    <div class="view-container">
      <AppMain />
    </div>
  </div>
</template>

<script setup lang="ts">
import {  Sidebar, AppMain } from '../components'
</script>
<style lang="scss" scoped>
@import './index.scss';

</style>
