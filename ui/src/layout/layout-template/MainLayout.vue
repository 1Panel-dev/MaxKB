<template>
  <div class="app-layout">
    <div class="app-header">
      <SystemHeader v-if="isShared"></SystemHeader>
      <UserHeader v-else />
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
import { computed } from 'vue'
import UserHeader from '@/layout/layout-header/UserHeader.vue'
import SystemHeader from '@/layout/layout-header/SystemHeader.vue'
import Sidebar from '@/layout/components/sidebar/index.vue'
import AppMain from '@/layout/app-main/index.vue'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
const route = useRoute()

const isShared = computed(() => {
  return route.path.endsWith('hared')
})
const { user } = useStore()
</script>
<style lang="scss" scoped>
@use './index.scss';
</style>
