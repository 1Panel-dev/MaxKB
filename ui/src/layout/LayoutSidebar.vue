<script setup lang="ts">
import SystemSidebar from './sidebar/SystemSidebar.vue'
import WorkspaceSidebar from './sidebar/WorkspaceSidebar.vue'
import { isSystem, isWorkspace } from '@/router/admin/utils'
import type { LayoutMode } from './types'

const props = defineProps<{
  mode: LayoutMode
  collapsed?: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()
</script>

<template>
  <aside
    class="flex h-layout-content shrink-0 flex-col overflow-hidden transition-[width] duration-200"
    :class="isSystem(mode) && !collapsed ? 'w-sidebar-expanded max-md:w-sidebar' : 'w-sidebar'"
  >
    <el-scrollbar class="min-h-0 flex-1">
      <WorkspaceSidebar v-if="isWorkspace(mode)" />
      <SystemSidebar v-if="isSystem(mode)" :collapsed="collapsed" />
    </el-scrollbar>

    <div
      v-if="isSystem(mode)"
      :class="props.collapsed ? 'px-2.5 pb-[18px]' : 'px-5 pb-[18px] max-md:px-2.5'"
    >
      <button
        type="button"
        class="flex h-[46px] w-full cursor-pointer items-center gap-2.5 px-1"
        @click="emit('toggle')"
      >
        <MkIcon name="icon_left_outlined" />
        <span :class="collapsed && 'hidden'" class="max-md:hidden">收起导航</span>
      </button>
    </div>
  </aside>
</template>
