<template>
  <div class="app-header" :class="!isDefaultTheme ? 'custom-header' : ''">
    <TopBar />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import TopBar from '../top-bar/index.vue'
import useStore from '@/stores'
const { user } = useStore()
const isDefaultTheme = computed(() => {
  return user.isDefaultTheme()
})
</script>

<style lang="scss" scoped>
.app-header {
  background: var(--app-header-bg-color);
  position: fixed;
  width: 100%;
  left: 0;
  top: 0;
  z-index: 100;
}
.custom-header {
  background: var(--el-color-primary-light-9) !important;
}
</style>
