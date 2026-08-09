<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import WorkspaceApi from '@/api/admin/system/workspace'
import type { WorkspaceItem, WorkspaceMemberItem } from '@/api/types'
import MkSearchList from '@/components/mk-search-list/index.vue'
import { Plus, UserFilled } from '@element-plus/icons-vue'

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
    <aside class="flex w-sidebar-expanded shrink-0 flex-col border-r">
      <header class="flex-between p-4">
        <h4>{{ route.meta.title }}</h4>
        <el-button text type="primary" class="-mr-1">
          <MkIcon name="icon_add_outlined" :size="18" />
        </el-button>
      </header>
      <MkSearchList
        :data="workspacesList"
        :default-active="currentWorkspace?.id"
        @click="currentWorkspace = $event"
      >
        <template #action-dropdown>
          <MkDropdownMenu>
            <MkDropdownItem>
              <template #icon>
                <MkIcon name="icon_edit_outlined" />
              </template>
              <span>重命名</span>
            </MkDropdownItem>
          </MkDropdownMenu>
          <el-divider />
          <MkDropdownMenu>
            <MkDropdownItem>
              <template #icon>
                <MkIcon name="icon_delete-trash_outlined" />
              </template>
              <span>删除</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkSearchList>
    </aside>

    <section class="min-w-0 flex-1 px-6">
      <header class="py-4">
        <div class="flex items-center gap-2">
          <h4>{{ currentWorkspace?.name }}</h4>
          <el-divider direction="vertical" />
          <span class="flex items-center text-N500">
            <MkIcon :icon="UserFilled" :size="16" class="mr-1" />
            {{ currentWorkspace?.user_count }}
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
