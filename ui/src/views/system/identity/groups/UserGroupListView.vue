<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import WorkspaceApi from '@/api/admin/system/workspace'
import type { RequestParams, OptionItem, WorkspaceItem } from '@/api/types'
import MkWorkspaceDropdown from '@/components/mk-workspace-dropdown/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'
import MkWorkspaceRelationTags from '@/components/mk-workspace-relation-tags/index.vue'

interface UserGroup {
  id: string
  memberCount: number
  name: string
}

interface UserGroupMember {
  id: number
  name: string
  roles: string[]
  source: string
  username: string
}

/* 成员列表相关 */
const paginationConfig = ref({
  currentPage: 2,
  pageSize: 10,
  total: 20,
})
const memberSearchQuery = ref<RequestParams>()
const memberSearchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'name' },
]
const userGroupMembers = ref<UserGroupMember[]>([
  { id: 1, name: 'test-w', username: 'test-w', roles: ['工作空间管理员'], source: '系统用户' },
  { id: 2, name: 'Eira1', username: 'Eira1', roles: ['普通用户', '管理员'], source: '钉钉' },
  { id: 3, name: '司马图南', username: 'simatunan', roles: ['普通用户'], source: '钉钉' },
  { id: 4, name: '吕晓', username: 'lvxiao', roles: ['usso-工作空间管理员'], source: 'CAS' },
  { id: 5, name: '涂晓', username: 'tuixao', roles: ['普通用户'], source: 'LDAP' },
  { id: 6, name: '裴尔', username: 'peier', roles: ['普通用户'], source: 'OIDC' },
  { id: 7, name: '裴尔尔', username: 'peierer', roles: ['普通用户'], source: 'OAuth2' },
  { id: 8, name: '裴晓尔', username: 'peixiaoer', roles: ['普通用户'], source: '企业微信' },
  { id: 9, name: 'shaohu', username: 'shaohu', roles: ['普通用户'], source: '企业微信' },
  { id: 10, name: '白新', username: 'baixin', roles: ['普通用户'], source: '飞书' },
])
function handleMemberSearch(query?: RequestParams) {
  memberSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  return
}

/* 选择用户组列表 */
const currentGroup = ref<UserGroup>()
const userGroups = ref<UserGroup[]>([
  { id: 'delivery', name: '交付', memberCount: 18 },
  { id: 'finance', name: '财务', memberCount: 20 },
  { id: 'development', name: '研发', memberCount: 36 },
  { id: 'marketing', name: '市场', memberCount: 24 },
  { id: 'sales', name: '销售', memberCount: 28 },
])
function handleGroupSelect(group: UserGroup) {
  currentGroup.value = group
  paginationConfig.value.currentPage = 1
  return
}

/* 选择工作空间列表 */
const selectedWorkspaceId = ref('default')
const workspaceOptions = ref<WorkspaceItem[]>([])

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
}

function loadWorkspaceOptions() {
  WorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
    workspaceOptions.value = workspaces

    if (!workspaceOptions.value.some(({ id }) => id === selectedWorkspaceId.value)) {
      selectedWorkspaceId.value = workspaceOptions.value[0]?.id ?? 'default'
    }
  })
}

onMounted(() => loadWorkspaceOptions())
</script>

<template>
  <div class="system-identity-groups flex h-full flex-col">
    <header class="border-b px-4 py-3">
      <MkWorkspaceDropdown
        v-model="selectedWorkspaceId"
        :options="workspaceOptions"
        @select="handleWorkspaceSelect"
      />
    </header>
    <div class="flex min-h-0 flex-1">
      <aside class="flex w-sidebar-expanded shrink-0 flex-col border-r">
        <header class="flex-between p-4">
          <h4>用户组</h4>
          <el-button class="-mr-1" text type="primary" @click="createUserGroup">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </header>

        <MkSearchList
          :data="userGroups"
          :default-active="currentGroup?.id"
          @click="handleGroupSelect"
        >
          <template #action-dropdown>
            <MkDropdownMenu>
              <MkDropdownItem>
                <template #icon>
                  <MkIcon name="icon_edit_outlined" />
                </template>
                <span>重命名</span>
              </MkDropdownItem>
              <el-divider />
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
      <section v-if="currentGroup" class="min-w-0 flex-1 px-6">
        <header class="flex h-14 items-center gap-2">
          <h4>{{ currentGroup?.name }}</h4>
          <el-divider direction="vertical" />
          <span class="flex items-center text-N500">
            <MkIcon name="icon_member_filled" class="mr-1" />
            {{ currentGroup?.memberCount }}
          </span>
        </header>

        <div class="flex-between mb-4">
          <el-button type="primary">
            <MkIcon name="icon_add_outlined" />
            <span>添加成员</span>
          </el-button>
          <MkComplexSearch :fields="memberSearchFields" @change="handleMemberSearch" />
        </div>

        <MkTable
          :max-table-height="340"
          v-model:pagination-config="paginationConfig"
          :data="userGroupMembers"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column prop="name" label="姓名" min-width="198" show-overflow-tooltip />
          <el-table-column prop="username" label="用户名" min-width="198" show-overflow-tooltip />
          <el-table-column label="角色" min-width="198">
            <template #default="{ row }">
              <MkWorkspaceRelationTags
                :table-render-params="{ property: '角色', value: '工作空间' }"
                :tags="row.role_name"
                :tag-workspace="row.role_workspace"
              />
            </template>
          </el-table-column>
          <el-table-column prop="source" label="用户来源" min-width="198" show-overflow-tooltip />
          <el-table-column label="操作" width="70" fixed="right">
            <template #default="{ row }">
              <el-tooltip effect="dark" content="移除" placement="top">
                <el-button type="primary" text>
                  <MkIcon name="icon_assigned_outlined" />
                </el-button>
              </el-tooltip>
            </template>
          </el-table-column>
          <template #footer-batch-actions>
            <el-button type="danger" plain @click="handleBatchDelete">移除</el-button>
          </template>
        </MkTable>
      </section>
    </div>
  </div>
</template>
