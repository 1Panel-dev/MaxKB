<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import SystemSidebar from './sidebar/SystemSidebar.vue'
import WorkspaceSidebar from './sidebar/WorkspaceSidebar.vue'
import { isSystem, isWorkspace } from './utils'
import type { LayoutMode } from './types'
import { useIsSmallScreen } from '@/utils/use-responsive'

const props = defineProps<{ mode: LayoutMode }>()

const route = useRoute()
const isSmallScreen = useIsSmallScreen()
const isSystemDetail = computed(() => isSystem(props.mode) && route.meta.resourceDetailRoot === true)
const collapsed = ref(false)

// 系统详情默认收起，离开详情恢复普通页面状态；小屏继续默认收起。
watch(
  [isSmallScreen, isSystemDetail],
  ([smallScreen, systemDetail]) => {
    collapsed.value = smallScreen || systemDetail
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
