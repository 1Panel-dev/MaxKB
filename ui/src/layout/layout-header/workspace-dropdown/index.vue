<template>
  <el-dropdown placement="bottom-start">
    <el-button text>
      <AppIcon iconName="app-wordspace" style="font-size: 18px"></AppIcon>
      <span class="dropdown-title ellipsis">
        {{ currentWorkspace?.name }}
      </span>
      <el-icon class="el-icon--right">
        <CaretBottom />
      </el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu v-loading="loading">
        <el-dropdown-item
          v-for="item in workspaceList"
          :key="item.id"
          :class="item.id === currentWorkspace?.id ? 'active' : ''"
          @click="changeWorkspace(item)"
        >
          <AppIcon class="mr-8" iconName="app-wordspace" style="font-size: 16px"></AppIcon>
          <span class="dropdown-item ellipsis">
            {{ item.name }}
          </span>
          <el-icon
            v-show="item.id === currentWorkspace?.id"
            class="ml-8"
            style="font-size: 16px; margin-right: 0"
          >
            <Check />
          </el-icon>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { onBeforeMount, ref } from 'vue'
import WorkspaceApi from '@/api/workspace/workspace'
import type { WorkspaceItem } from '@/api/type/workspace'
import useStore from '@/stores'
const { user } = useStore()
const loading = ref(false)
const workspaceList = ref<WorkspaceItem[]>([])
const currentWorkspace = ref()

async function getWorkspaceList() {
  try {
    const res = await WorkspaceApi.getWorkspaceListByUser(loading)
    workspaceList.value = res.data
  } catch (e) {
    console.error(e)
  }
}

onBeforeMount(async () => {
  await getWorkspaceList()
  const id = localStorage.getItem('workspace_id') ?? 'default'
  currentWorkspace.value = workspaceList.value.find((item) => item.id === id)
})

function changeWorkspace(item: WorkspaceItem) {
  if (item.id === currentWorkspace.value.id) return
  currentWorkspace.value = item
  user.setWorkspaceId(item.id || 'default')
  window.location.reload()
}
</script>
<style lang="scss" scoped>
:deep(.el-button.is-text) {
  color: var(--el-text-color-primary);
  max-height: 32px;
}

.dropdown-title {
  max-width: 155px;
  font-size: 14px;
}

.dropdown-item {
  max-width: 230px;
}

:deep(.el-dropdown-menu__item.active) {
  color: var(--el-color-primary);
}
</style>
