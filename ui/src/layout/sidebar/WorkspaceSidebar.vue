<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getChildRouteList } from '@/router/admin/utils'
import type { LayoutMenuItem } from '@/types'

const route = useRoute()
const router = useRouter()
const workspaceMenuItems = getChildRouteList('workspace')
const workspaceActiveMenuName = computed(() => route.meta.activeMenu ?? String(route.name ?? ''))

const isWorkspaceMenuActive = (workspaceMenuItem: LayoutMenuItem) =>
  workspaceMenuItem.name === workspaceActiveMenuName.value

function navigateToWorkspaceMenu(workspaceMenuItem: LayoutMenuItem) {
  if (!workspaceMenuItem.route) return
  void router.push({
    name: workspaceMenuItem.name,
    params: { workspaceId: route.params.workspaceId },
  })
}
</script>

<template>
  <div class="flex flex-col gap-1 p-1">
    <div
      v-for="workspaceMenuItem in workspaceMenuItems"
      :key="workspaceMenuItem.name"
      class="flex-col-center w-full cursor-pointer rounded-md py-2 text-xs font-semibold text-N600"
      :class="isWorkspaceMenuActive(workspaceMenuItem) && 'bg-white text-N900'"
      @click="navigateToWorkspaceMenu(workspaceMenuItem)"
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
