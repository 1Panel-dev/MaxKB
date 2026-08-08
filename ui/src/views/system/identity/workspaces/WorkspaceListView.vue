<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import WorkspaceApi from '@/api/admin/system/workspace'
import type { WorkspaceItem, WorkspaceMemberItem } from '@/types'
import { Delete, EditPen, MoreFilled, Plus, UserFilled } from '@element-plus/icons-vue'

const route = useRoute()
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 240,
})

const workspaceMembers: WorkspaceMemberItem[] = []

/* 选择工作空间列表 */
const currentWorkspace = ref<WorkspaceItem>()
const workspacesList = ref<WorkspaceItem[]>([])

function handleWorkspaceCommand() {}

function loadWorkspaceOptions() {
  WorkspaceApi.getSystemWorkspaceList().then((res) => {
    workspacesList.value = res
  })
}
onMounted(async () => {
  await loadWorkspaceOptions()
  currentWorkspace.value = workspacesList.value[0]
})
</script>

<template>
  <div class="system-identity-workspaces flex h-full">
    <aside class="flex w-60 shrink-0 flex-col border-r p-4">
      <header class="flex-between mb-4">
        <h4>{{ route.meta.title }}</h4>
        <el-button text type="primary">
          <MkIcon name="icon_add_outlined" :size="18" />
        </el-button>
      </header>
      <MkSearchList>
        <div class="flex flex-col gap-1">
          <div
            v-for="workspace in workspacesList"
            :key="workspace.id"
            class="h-10 flex items-center rounded-md px-2"
          >
            <span class="min-w-0 flex-1 truncate">{{ workspace.name }}</span>

            <MkDropdown class="-mr-1" trigger="click">
              <el-button text @click.stop>
                <MkIcon :icon="MoreFilled" />
              </el-button>
              <template #dropdown>
                <MkDropdownMenu>
                  <MkDropdownItem command="rename" :icon="EditPen">重命名</MkDropdownItem>
                  <MkDropdownItem command="delete" :icon="Delete">删除</MkDropdownItem>
                </MkDropdownMenu>
              </template>
            </MkDropdown>
          </div>
        </div>
      </MkSearchList>
    </aside>

    <section class="min-w-0 flex-1 px-6">
      <header class="py-4">
        <div class="flex items-center gap-2">
          <h4>{{ currentWorkspace?.name }}</h4>
          <el-divider direction="vertical" />
          <span class="flex items-center text-N500">
            <MkIcon :icon="UserFilled" :size="16" class="mr-1" />
            {{ currentWorkspace?.memberCount }}
          </span>
        </div>
      </header>
      <div class="mb-4">
        <el-button type="primary" :icon="Plus">添加成员</el-button>
      </div>

      <MkTable
        v-model:pagination-config="paginationConfig"
        :data="workspaceMembers"
        :max-table-height="320"
        row-key="id"
      >
        <el-table-column type="selection" width="64" />
        <el-table-column prop="name" label="姓名" min-width="220" show-overflow-tooltip />
        <el-table-column prop="username" label="用户名" min-width="220" show-overflow-tooltip />
      </MkTable>
    </section>
  </div>
</template>
