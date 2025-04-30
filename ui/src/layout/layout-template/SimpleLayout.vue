<script setup lang="ts">
import UserHeader from '@/layout/layout-header/UserHeader.vue'
import AppMain from '@/layout/app-main/index.vue'
</script>

<template>
  <div class="app-layout">
    <div class="app-header">
      <UserHeader />
    </div>
    <div class="app-main">
      <AppMain />
    </div>
  </div>
</template>
<style lang="scss">
@use './index.scss';
</style>
