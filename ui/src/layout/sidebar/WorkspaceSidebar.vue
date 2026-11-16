<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { LayoutMenuItem } from '../types'
import { getChildRouteList } from '@/router/admin/utils'

const { t, te } = useI18n({ useScope: 'global' })

const route = useRoute()
const router = useRouter()
const workspaceMenuItems = computed(() => getChildRouteList('workspace', (title) => (te(title) ? t(title) : title)))
const workspaceActiveMenuName = computed(() => route.meta.activeMenu ?? String(route.name ?? ''))

const isWorkspaceMenuActive = (workspaceMenuItem: LayoutMenuItem) => workspaceMenuItem.name === workspaceActiveMenuName.value

function navigateToWorkspaceMenu(workspaceMenuItem: LayoutMenuItem) {
  if (!workspaceMenuItem.route) return
  void router.push({ name: workspaceMenuItem.name, params: { workspaceId: route.params.workspaceId } })
}
</script>

<template>
  <div class="space-y-1 p-1">
    <template v-for="workspaceMenuItem in workspaceMenuItems" :key="workspaceMenuItem.name">
      <div
        v-if="workspaceMenuItem.permission ? workspaceMenuItem.permission(route) : true"
        class="flex-col-center w-full cursor-pointer rounded-md py-2 text-xs font-semibold text-N600"
        :class="isWorkspaceMenuActive(workspaceMenuItem) ? 'bg-white text-N900' : 'hover:bg-N900/10'"
        @click="navigateToWorkspaceMenu(workspaceMenuItem)"
      >
        <MkIcon
          v-if="workspaceMenuItem.icon"
          :name="isWorkspaceMenuActive(workspaceMenuItem) ? (workspaceMenuItem.activeIcon ?? workspaceMenuItem.icon) : workspaceMenuItem.icon"
          :gradient="isWorkspaceMenuActive(workspaceMenuItem)"
        />
        <span class="mt-[2px]">{{ workspaceMenuItem.label }}</span>
      </div>
    </template>
  </div>
</template>
