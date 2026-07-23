<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import LayoutHeader from './LayoutHeader.vue'
import LayoutSidebar from './LayoutSidebar.vue'
import type { LayoutMode } from './types'

const route = useRoute()

const mode = computed<LayoutMode>(() => route.meta.scope ?? 'workspace')
</script>

<template>
  <div class="mk-layout h-screen overflow-hidden bg-layout-gradient">
    <LayoutHeader :mode="mode"> </LayoutHeader>
    <div class="flex">
      <LayoutSidebar :mode="mode" />
      <main
        class="h-layout-content w-full overflow-hidden rounded-tl-xl bg-white transition-[margin] duration-200"
      >
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
