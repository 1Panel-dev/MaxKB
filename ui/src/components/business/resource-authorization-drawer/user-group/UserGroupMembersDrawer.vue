<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import UserGroupsApi from '@/api/admin/system/user-groups'
import { LOGIN_METHOD } from '@/api/enums'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { useStore } from '@/stores'
import type { Dict, LoginMethod, OptionItem, SystemUserGroup, SystemUserGroupMember } from '@/api/types'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'UserGroupMembersDrawer' })

/* 成员查询与分页 */
const { auth } = useStore()
const drawerVisible = ref(false)
const currentGroup = ref<SystemUserGroup>()
const loadingMembers = ref(false)
const userGroupMembers = ref<SystemUserGroupMember[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const memberSearchQuery = ref<Dict<unknown>>()
const memberSearchFields = computed<OptionItem<string>[]>(() => [
  { label: t('system.identity.users.fields.name'), value: 'nick_name' },
  { label: t('system.identity.users.fields.username'), value: 'username' },
  ...(auth.isEE || auth.isPE ? [{ label: t('system.identity.roles.label'), value: 'role' }] : []),
])

/* 表头筛选 */
const selectedMemberSource = ref<string | null>(null)
const memberSourceOptions = computed<OptionItem<string>[]>(() =>
  Object.entries(LOGIN_METHOD_LABELS).map(([value, label]) => ({
    label: value === LOGIN_METHOD.LOCAL ? t('system.identity.users.sources.system') : label,
    value,
  })),
)
const memberListQuery = computed<Dict<unknown>>(() => ({
  ...memberSearchQuery.value,
  ...(selectedMemberSource.value !== null ? { source: selectedMemberSource.value } : {}),
}))

function loadUserGroupMembers() {
  const group = currentGroup.value
  if (!group) return

  loadingMembers.value = true
  return UserGroupsApi.getSystemUserGroupMembers(group.workspace_id, group.id, paginationConfig.value, memberListQuery.value)
    .then(({ records, total }) => {
      userGroupMembers.value = records
      paginationConfig.value.total = total
      if (!memberSearchQuery.value && selectedMemberSource.value === null) group.count = total
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

function handleMemberFilterChange() {
  paginationConfig.value.currentPage = 1
  loadUserGroupMembers()
}

function open(userGroup: SystemUserGroup) {
  resetData()
  currentGroup.value = { ...userGroup }
  drawerVisible.value = true
  loadUserGroupMembers()
}

/* 抽屉生命周期 */
function resetData() {
  currentGroup.value = undefined
  loadingMembers.value = false
  userGroupMembers.value = []
  paginationConfig.value = { currentPage: 1, pageSize: 20, total: 0 }
  memberSearchQuery.value = undefined
  selectedMemberSource.value = null
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="drawerVisible" :title="currentGroup?.name" @closed="resetData">
    <template #header>
      <div class="flex-align-center min-w-0 gap-2">
        <h4 class="min-w-0 truncate" :title="currentGroup?.name">{{ currentGroup?.name }}</h4>
        <el-divider direction="vertical" />
        <span class="flex-align-center shrink-0 text-N500">
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
      <el-table-column prop="nick_name" :label="t('system.identity.users.fields.name')" show-overflow-tooltip />
      <el-table-column prop="username" :label="t('system.identity.users.fields.username')" show-overflow-tooltip />
      <el-table-column prop="source" :label="t('system.identity.users.fields.source')">
        <template #header>
          <MkTableFilter
            mode="single"
            v-model="selectedMemberSource"
            :label="t('system.identity.users.fields.source')"
            :options="memberSourceOptions"
            @change="handleMemberFilterChange"
          />
        </template>
        <template #default="{ row }">
          {{ row.source === LOGIN_METHOD.LOCAL ? t('system.identity.users.sources.system') : LOGIN_METHOD_LABELS[row.source as LoginMethod] }}
        </template>
      </el-table-column>
      <el-table-column v-if="auth.isEE || auth.isPE" :label="t('system.identity.roles.label')">
        <template #default="{ row }">
          <MkTagGroup v-if="row.roles?.length" :tags="row.roles" />
          <span v-else>-</span>
        </template>
      </el-table-column>
    </MkTable>
  </MkDrawer>
</template>
