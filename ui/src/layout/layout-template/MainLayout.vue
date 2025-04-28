<template>
  <div class="app-layout">
    <div class="app-header">
      <UserHeader />
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
import UserHeader from '@/layout/layout-header/UserHeader.vue'
import Sidebar from '@/layout/components/sidebar/index.vue'
import AppMain from '@/layout/app-main/index.vue'
import useStore from '@/stores'
const { user } = useStore()
</script>
<style lang="scss" scoped>
@import './index.scss';
</style>
