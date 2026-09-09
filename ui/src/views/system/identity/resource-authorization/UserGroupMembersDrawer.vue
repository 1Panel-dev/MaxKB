<script setup lang="ts">
import { ref } from 'vue'
import UserGroupsApi from '@/api/admin/system/user-groups'
import type { Dict, OptionItem, SystemUserGroup, SystemUserGroupMember } from '@/api/types'

/* 成员查询与分页 */
const drawerVisible = ref(false)
const currentGroup = ref<SystemUserGroup>()
const loadingMembers = ref(false)
const userGroupMembers = ref<SystemUserGroupMember[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 10, total: 0 })
const memberSearchQuery = ref<Dict<unknown>>()
const memberSearchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
]

function loadUserGroupMembers() {
  const group = currentGroup.value
  if (!group) return

  loadingMembers.value = true
  return UserGroupsApi.getSystemUserGroupMembers(group.workspace_id, group.id, paginationConfig.value, memberSearchQuery.value)
    .then(({ records, total }) => {
      userGroupMembers.value = records
      paginationConfig.value.total = total
      if (!memberSearchQuery.value) group.count = total
    })
    .finally(() => {
      loadingMembers.value = false
    })
}

function handleMemberSearch(query?: Dict<unknown>) {
  memberSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  loadUserGroupMembers()
}

function open(userGroup: SystemUserGroup) {
  currentGroup.value = { ...userGroup }
  drawerVisible.value = true
  loadUserGroupMembers()
}

/* 抽屉生命周期 */
function resetData() {
  currentGroup.value = undefined
  loadingMembers.value = false
  userGroupMembers.value = []
  paginationConfig.value = { currentPage: 1, pageSize: 10, total: 0 }
  memberSearchQuery.value = undefined
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="drawerVisible" :title="currentGroup?.name" @closed="resetData">
    <template #header>
      <div class="flex min-w-0 items-center gap-2">
        <h4 class="min-w-0 truncate" :title="currentGroup?.name">{{ currentGroup?.name }}</h4>
        <el-divider direction="vertical" />
        <span class="flex shrink-0 items-center text-N500">
          <MkIcon name="icon_member_filled" class="mr-1" />
          {{ currentGroup?.count }}
        </span>
      </div>
    </template>

    <MkComplexSearch class="mb-4 w-[50%]" :fields="memberSearchFields" @change="handleMemberSearch" />
    <MkTable
      v-loading="loadingMembers"
      v-model:pagination-config="paginationConfig"
      :data="userGroupMembers"
      :max-table-height="220"
      @current-change="loadUserGroupMembers"
      @size-change="loadUserGroupMembers"
    >
      <el-table-column prop="nick_name" label="姓名" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" show-overflow-tooltip />
      <el-table-column label="角色">
        <template #default="{ row }">
          <MkTagGroup v-if="row.roles?.length" :tags="row.roles" />
          <span v-else>-</span>
        </template>
      </el-table-column>
    </MkTable>
  </MkDrawer>
</template>
