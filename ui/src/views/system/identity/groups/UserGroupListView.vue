<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Plus, User, UserFilled } from '@element-plus/icons-vue'
import WorkspaceApi from '@/api/admin/system/workspace'
import MkWorkspaceDropdown from '@/components/mk-workspace-dropdown/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'

import type { OptionItem, WorkspaceItem } from '@/api/types'
import { MsgConfirm, MsgInfo, MsgSuccess } from '@/utils/message'

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

const memberSearchQuery = ref<Record<string, boolean | number | string>>()
const memberSearchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'name' },
]
const selectedGroupId = ref('finance')
const paginationConfig = ref({
  currentPage: 2,
  pageSize: 10,
  total: 20,
})
const userGroups = ref<UserGroup[]>([
  { id: 'delivery', name: '交付', memberCount: 18 },
  { id: 'finance', name: '财务', memberCount: 20 },
  { id: 'development', name: '研发', memberCount: 36 },
  { id: 'marketing', name: '市场', memberCount: 24 },
  { id: 'sales', name: '销售', memberCount: 28 },
])
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
const selectedUserGroup = computed(() => {
  return userGroups.value.find(({ id }) => id === selectedGroupId.value)
})

const filteredUserGroupMembers = computed(() => {
  const [field, value] = Object.entries(memberSearchQuery.value ?? {})[0] ?? []
  const keyword = String(value ?? '')
    .trim()
    .toLowerCase()

  if (!field || !keyword) return userGroupMembers.value

  return userGroupMembers.value.filter((member) => {
    if (field !== 'name' && field !== 'username') return true
    return member[field].toLowerCase().includes(keyword)
  })
})

async function createUserGroup() {
  const groupName = `用户组 ${userGroups.value.length + 1}`
  const group = { id: `group-${Date.now()}`, memberCount: 0, name: groupName }

  userGroups.value.push(group)
  selectedGroupId.value = group.id
  MsgSuccess('用户组创建成功')
}

function addMember() {
  MsgInfo('添加成员功能待接入')
}

function addMemberToGroup(member: UserGroupMember) {
  MsgSuccess(`已将“${member.name}”添加到用户组`)
}

/* 选择工作空间列表 */
const selectedWorkspaceId = ref('default')
const workspaceOptions = ref<WorkspaceItem[]>([])

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
  selectedGroupId.value = userGroups.value[0]?.id ?? ''
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
          :default-active="selectedGroupId"
          @click="selectedGroupId = $event.id"
        >
          <template #action-dropdown="{ row: group }">
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
      <section v-if="selectedUserGroup" class="min-w-0 flex-1 px-6">
        <header class="flex h-14 items-center gap-2">
          <h4>{{ selectedUserGroup.name }}</h4>
          <el-divider direction="vertical" />
          <span class="flex items-center text-N500">
            <MkIcon :icon="UserFilled" class="mr-1" />
            {{ selectedUserGroup.memberCount }}
          </span>
        </header>

        <div class="flex-between mb-4">
          <el-button type="primary" :icon="Plus" @click="addMember">添加成员</el-button>
          <MkComplexSearch :fields="memberSearchFields" @change="memberSearchQuery = $event" />
        </div>

        <MkTable
          v-model:pagination-config="paginationConfig"
          :data="filteredUserGroupMembers"
          :max-table-height="330"
          row-key="id"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column prop="name" label="姓名" min-width="198" show-overflow-tooltip />
          <el-table-column prop="username" label="用户名" min-width="198" show-overflow-tooltip />
          <el-table-column label="角色" min-width="198">
            <template #default="{ row }: { row: UserGroupMember }">
              <div class="flex items-center gap-1">
                <el-tag effect="plain" type="info">{{ row.roles[0] }}</el-tag>
                <el-tag v-if="row.roles.length > 1" effect="plain" type="info">
                  +{{ row.roles.length - 1 }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="用户来源" min-width="198" show-overflow-tooltip />
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ row }: { row: UserGroupMember }">
              <el-button
                text
                type="primary"
                :icon="User"
                aria-label="添加到用户组"
                @click="addMemberToGroup(row)"
              />
            </template>
          </el-table-column>
        </MkTable>
      </section>
    </div>
  </div>
</template>
