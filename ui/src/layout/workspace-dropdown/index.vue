<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MkFilterableDropdown from '@/components/mk-filterable-dropdown/index.vue'
import { ArrowDown, Collection } from '@element-plus/icons-vue'
import { useStore } from '@/stores'

/**
 * 工作空间下拉框。
 * 负责加载工作空间数据、维护当前工作空间，并组合通用的筛选下拉组件。
 */
defineOptions({ name: 'WorkspaceDropdown' })

const route = useRoute()
const router = useRouter()
const { user } = useStore()

const selectedWorkspace = computed<string | number>({
  get: () => user.workspaceId,
  set: (workspaceId) => {
    const normalizedWorkspaceId = String(workspaceId)
    if (normalizedWorkspaceId === user.workspaceId || !route.name) return
    void router.push({
      name: route.name,
      params: { ...route.params, workspaceId: normalizedWorkspaceId },
      query: route.query,
      hash: route.hash,
    })
  },
})
</script>

<template>
  <MkFilterableDropdown
    v-model="selectedWorkspace"
    :options="workspaceOptions"
    placeholder="请选择工作空间"
  >
    <template #default="{ text }">
      <button type="button" class="flex max-w-50 items-center gap-1 rounded-md px-2 py-1">
        <MkIcon :icon="Collection" />
        <span class="min-w-0 flex-1 truncate">{{ text }}</span>
        <MkIcon :icon="ArrowDown" class="shrink-0" />
      </button>
    </template>

    <template #option="{ option }">
      <div class="flex items-center gap-2">
        <MkIcon :icon="Collection" />
        <span class="min-w-0 flex-1 truncate">{{ option.label }}</span>
      </div>
    </template>
  </MkFilterableDropdown>
</template>
