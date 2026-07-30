<script setup lang="ts">
import { computed, h, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Delete, EditPen, MoreFilled, Plus, Search, UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MkIcon from '@/components/global/mk-icon/index.vue'

interface SystemWorkspace {
  id: string
  memberCount: number
  name: string
}

interface WorkspaceMember {
  id: number
  name: string
  username: string
}

type WorkspaceAction = 'delete' | 'rename'

const route = useRoute()
const searchKeyword = ref('')
const selectedWorkspaceId = ref('workspace-2')
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 240,
})
const systemWorkspaces = ref<SystemWorkspace[]>([
  { id: 'default', name: '默认工作空间', memberCount: 36 },
  { id: 'dataease', name: 'DataEase 工作空间', memberCount: 42 },
  { id: 'jumpserver', name: 'Jumpserver 工作空间', memberCount: 28 },
  { id: 'maxkb', name: 'MaxKB 工作空间', memberCount: 54 },
  { id: 'workspace-1', name: '工作空间 1', memberCount: 40 },
  { id: 'workspace-2', name: '工作空间 2', memberCount: 240 },
])
const workspaceMembers: WorkspaceMember[] = [
  { id: 1, name: 'test-w', username: 'test-w' },
  { id: 2, name: 'Eira1', username: 'Eira1' },
  { id: 3, name: '司马图南', username: 'simatunan' },
  { id: 4, name: '吕晓', username: 'lvxiao' },
  { id: 5, name: '涂晓', username: 'tuixao' },
  { id: 6, name: '裴尔', username: 'peier' },
  { id: 7, name: '裴尔尔', username: 'peierer' },
  { id: 8, name: '裴晓尔', username: 'peixiaoer' },
  { id: 9, name: 'shaohu', username: 'shaohu' },
  { id: 10, name: '白新', username: 'baixin' },
]

const filteredWorkspaces = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  if (!keyword) {
    return systemWorkspaces.value
  }

  return systemWorkspaces.value.filter((workspace) =>
    workspace.name.toLowerCase().includes(keyword),
  )
})

const selectedWorkspace = computed(() => {
  return systemWorkspaces.value.find((workspace) => workspace.id === selectedWorkspaceId.value)
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
      <div>
        <el-input
          v-model="searchKeyword"
          clearable
          placeholder="搜索"
          class="mb-2"
        >
          <template #prefix>
            <MkIcon name="icon_search-outlined" />
          </template>
        </el-input>
        <el-scrollbar>
          <div class="flex flex-col gap-1">
            <div
              v-for="workspace in filteredWorkspaces"
              :key="workspace.id"
              class="h-10 flex items-center rounded-md px-2"
              @click="selectedWorkspaceId = workspace.id"
              @keydown.enter="selectedWorkspaceId = workspace.id"
            >
              <span class="min-w-0 flex-1 truncate">{{ workspace.name }}</span>

              <MkDropdown
                class="-mr-1"
                trigger="click"
                @command="handleWorkspaceCommand($event, workspace.id)"
              >
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
        </el-scrollbar>
      </div>
    </aside>

    <div class="min-w-0 flex-1 px-6">
      <header class="py-4">
        <div class="flex items-center gap-2">
          <h4>{{ selectedWorkspace.name }}</h4>
          <el-divider direction="vertical" />
          <span class="flex items-center text-N500">
            <MkIcon :icon="UserFilled" :size="16" class="mr-1" />
            {{ selectedWorkspace.memberCount }}
          </span>
        </div>
      </header>
      <div class="mb-4">
        <el-button type="primary" :icon="Plus" @click="addMember">添加成员</el-button>
      </div>

      <MkTable
        v-model:pagination-config="paginationConfig"
        :data="workspaceMembers"
        max-height="612"
        row-key="id"
      >
        <el-table-column type="selection" width="64" />
        <el-table-column prop="name" label="姓名" min-width="220" show-overflow-tooltip />
        <el-table-column prop="username" label="用户名" min-width="220" show-overflow-tooltip />
      </MkTable>
    </div>
  </div>
</template>
