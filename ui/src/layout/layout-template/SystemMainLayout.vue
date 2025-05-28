<template>
  <div class="app-layout">
    <div class="app-header">
      <SystemHeader />
    </div>
    <div class="app-main">
      <layout-container>
        <template #left>
          <Sidebar />
        </template>
        <AppMain />
      </layout-container>
    </div>
  </div>
</template>
<script setup lang="ts">
import SystemHeader from '@/layout/layout-header/SystemHeader.vue'
import Sidebar from '@/layout/components/sidebar/index.vue'
import AppMain from '@/layout/app-main/index.vue'
import useStore from '@/stores'
const { user } = useStore()
</script>
<style lang="scss" scoped>
@use './index.scss';
</style>
