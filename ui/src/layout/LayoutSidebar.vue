<script setup lang="ts">
import { ref, watch } from 'vue'
import SystemSidebar from './sidebar/SystemSidebar.vue'
import WorkspaceSidebar from './sidebar/WorkspaceSidebar.vue'
import { isSystem, isWorkspace } from '@/router/admin/utils'
import { useIsSmallScreen } from '@/utils/use-responsive'
import type { LayoutMode } from './types'

defineProps<{
  mode: LayoutMode
}>()

const isSmallScreen = useIsSmallScreen()
const collapsed = ref(false)

watch(
  isSmallScreen,
  (smallScreen) => {
    collapsed.value = smallScreen
  },
  { immediate: true },
)
</script>

<template>
  <aside
    class="h-layout-content shrink-0 overflow-hidden transition-[width] duration-200"
    :class="isSystem(mode) && !collapsed ? 'w-sidebar-expanded' : 'w-sidebar'"
  >
    <WorkspaceSidebar v-if="isWorkspace(mode)" />
    <SystemSidebar v-if="isSystem(mode)" :collapsed="collapsed" @toggle="collapsed = !collapsed" />
  </aside>
</template>
