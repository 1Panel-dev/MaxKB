<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getChildRouteList } from '@/router/admin/utils'
import type { LayoutMenuItem } from '@/layout/types'

const route = useRoute()
const router = useRouter()
const workspaceMenuItems = getChildRouteList('workspace')
const workspaceActiveMenuPath = computed(() => route.meta.activeMenu ?? route.path)

const isWorkspaceMenuActive = (workspaceMenuItem: LayoutMenuItem) =>
  Boolean(
    workspaceMenuItem.route &&
    router.resolve(workspaceMenuItem.route).path === workspaceActiveMenuPath.value,
  )
</script>

<template>
  <div class="flex flex-col gap-1 p-1">
    <div
      v-for="workspaceMenuItem in workspaceMenuItems"
      :key="workspaceMenuItem.name"
      class="flex-col-center w-full cursor-pointer rounded-md py-2 text-xs font-semibold text-N600"
      :class="isWorkspaceMenuActive(workspaceMenuItem) && 'bg-white text-N900'"
      @click="workspaceMenuItem.route && router.push(workspaceMenuItem.route)"
    >
      <MkIcon
        v-if="workspaceMenuItem.icon"
        :name="
          isWorkspaceMenuActive(workspaceMenuItem)
            ? (workspaceMenuItem.activeIcon ?? workspaceMenuItem.icon)
            : workspaceMenuItem.icon
        "
        :gradient="isWorkspaceMenuActive(workspaceMenuItem)"
      />
      <span class="mt-[2px]">{{ workspaceMenuItem.label }}</span>
    </div>
  </div>
</template>
