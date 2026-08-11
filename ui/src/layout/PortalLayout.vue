<script setup lang="ts">
import { RouterView } from 'vue-router'
import LayoutHeader from './LayoutHeader.vue'
</script>

<template>
  <div class="mk-portal-layout h-screen overflow-hidden bg-layout-gradient">
    <LayoutHeader mode="workspace" />
    <main class="h-[calc(100vh-var(--header-h,56px))] overflow-hidden bg-white">
      <RouterView />
    </main>
  </div>
</template>

<style scoped lang="scss"></style>
