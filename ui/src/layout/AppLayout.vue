<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import type { LayoutMode } from './types'
import LayoutHeader from './LayoutHeader.vue'
import LayoutSidebar from './LayoutSidebar.vue'

const route = useRoute()

withDefaults(defineProps<{ preview?: boolean }>(), { preview: false })

const mode = computed<LayoutMode>(() => route.meta.scope ?? 'workspace')
</script>

<template>
  <div class="mk-layout overflow-hidden" :class="preview ? 'h-full' : 'h-screen'">
    <LayoutHeader :mode="preview ? 'workspace' : mode" :preview="preview" />
    <div class="flex">
      <aside v-if="preview" class="h-layout-content w-sidebar"></aside>
      <LayoutSidebar v-else :mode="mode" />
      <main class="mk-layout__main h-layout-content w-full overflow-hidden rounded-tl-xl bg-white transition-[margin] duration-200">
        <RouterView v-if="!preview" />
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
