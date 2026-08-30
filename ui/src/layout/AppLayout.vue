<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import type { LayoutMode } from './types'
import LayoutHeader from './LayoutHeader.vue'
import LayoutSidebar from './LayoutSidebar.vue'

const route = useRoute()

const mode = computed<LayoutMode>(() => route.meta.scope ?? 'workspace')
</script>

<template>
  <div class="mk-layout h-screen overflow-hidden">
    <LayoutHeader :mode="mode"> </LayoutHeader>
    <div class="flex">
      <LayoutSidebar :mode="mode" />
      <main class="mk-layout__main h-layout-content w-full overflow-hidden rounded-tl-xl bg-white transition-[margin] duration-200">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
.mk-layout {
  background: rgb(var(--mk-primary-rgb) / 5%);

  &__main {
    box-shadow: 0px 0px 4px 0px rgb(var(--mk-N900-rgb) / 2%);
  }
}
</style>
