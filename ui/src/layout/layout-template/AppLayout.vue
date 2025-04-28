<script setup lang="ts">
import UserHeader from './layout-header/UserHeader.vue'
import useStore from '@/stores'
const { user } = useStore()
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
@import './index.scss';
</style>
