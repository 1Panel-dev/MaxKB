<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '@/stores'
import UserManageApi from '@/api/admin/system/user-manage'
import type {
  LoginMethod,
  OptionItem,
  SystemUser,
  SystemUserQuery,
} from '@/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import { LOGIN_METHOD_LABELS } from '@/constants/auth.ts'
import UserFromDrawer from './components/UserFromDrawer.vue'
import RoleWorkspaceTag from './components/RoleWorkspaceTag.vue'

const { auth } = useStore()
const route = useRoute()

/* 创建用户啊 */
const userFormDrawerRef = ref<InstanceType<typeof UserFromDrawer>>()

/* 批量删除 */
const batchSelectedUsers = ref<SystemUser[]>([])
function handleBatchDelete() {
  const selectedUserIds = batchSelectedUsers.value.map(({ id }) => id)
  MsgConfirm('批量删除用户', `确定删除选中的 ${batchSelectedUsers.value.length} 个用户吗？`, {
    confirmButtonClass: 'danger',
    confirmButtonText: '删除',
  })
    .then(() => {
      systemUsersLoading.value = true

      return UserManageApi.postBatchDeleteUsers(selectedUserIds).then(async () => {
        MsgSuccess('删除成功')
        await loadSystemUsers()
        userTableRef.value?.clearSelection()
      })
    })

    .catch(() => {})
    .finally(() => {
      systemUsersLoading.value = false
    })
}

function handleBatchSelectionChange(selection: unknown[]) {
  batchSelectedUsers.value = selection as SystemUser[]
}

/* 列表查询相关 */
const userTableRef = useTemplateRef('userTableRef')
const searchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
  { label: '邮箱', value: 'email' },
  {
    label: '状态',
    value: 'is_active',
    options: [
      { label: '启用', value: true },
      { label: '禁用', value: false },
    ],
  },
]
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})
const systemUsersData = ref<SystemUser[]>([])
const systemUsersLoading = ref(false)
const systemUserQuery = ref<SystemUserQuery>()

function handleSearchChange(query?: SystemUserQuery) {
  systemUserQuery.value = query
  paginationConfig.value.currentPage = 1
  loadSystemUsers()
}

function handlePageSizeChange() {
  paginationConfig.value.currentPage = 1
  loadSystemUsers()
}
function loadSystemUsers() {
  systemUsersLoading.value = true
  return UserManageApi.getUserManagePage(paginationConfig.value, systemUserQuery.value)
    .then((res) => {
      systemUsersData.value = res.records
      paginationConfig.value = {
        currentPage: res.current,
        pageSize: res.size,
        total: res.total,
      }
    })
    .finally(() => {
      systemUsersLoading.value = false
    })
}

onMounted(() => loadSystemUsers())
</script>

<template>
  <div class="system-identity-users px-6">
    <header class="flex-between py-4">
      <h4>{{ route.meta.title }}</h4>
      <div class="flex items-center gap-3">
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
        <el-button>
          <MkIcon name="icon_import_outlined" />
          <span>导入用户</span>
        </el-button>
        <el-button type="primary" @click="userFormDrawerRef?.open()">
          <MkIcon name="icon_add_outlined" />
          <span>创建用户</span>
        </el-button>
      </div>
    </header>

    <MkTable
      ref="userTableRef"
      v-model:pagination-config="paginationConfig"
      :data="systemUsersData"
      v-loading="systemUsersLoading"
      row-key="id"
      @current-change="loadSystemUsers"
      @selection-change="handleBatchSelectionChange"
      @size-change="handlePageSizeChange"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="nick_name" label="姓名" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" show-overflow-tooltip />
      <el-table-column width="100" label="状态">
        <template #default="{ row }">
          <MkStatusLabel :active="row.is_active" />
        </template>
      </el-table-column>

      <el-table-column prop="email" label="邮箱" show-overflow-tooltip min-width="180">
        <template #default="{ row }">
          {{ row.email || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" width="120" label="手机号">
        <template #default="{ row }">
          {{ row.phone || '-' }}
        </template>
      </el-table-column>

      <el-table-column v-if="auth.isEE || auth.isPE" prop="role_name" width="210" label="角色">
        <template #default="{ row }">
          <RoleWorkspaceTag
            first-column-label="角色"
            first-column-prop="roleName"
            second-column-label="工作空间"
            second-column-prop="workspace"
            :tag-names="row.role_name"
            :tag-workspace="row.role_workspace"
          />
        </template>
      </el-table-column>

      <el-table-column prop="user_group_names" width="210" label="用户组">
        <template #default="{ row }">
          <RoleWorkspaceTag
            first-column-label="用户组"
            first-column-prop="userGroupName"
            second-column-label="工作空间"
            second-column-prop="workspace"
            :tag-names="row.user_group_names"
            :tag-workspace="row.role_workspace"
          />
        </template>
      </el-table-column>

      <el-table-column label="用户来源">
        <template #default="{ row }">
          {{ row.source === 'LOCAL' ? '系统用户' : LOGIN_METHOD_LABELS[row.source as LoginMethod] }}
        </template>
      </el-table-column>

      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <div class="flex items-center gap-3">
            <span @click.stop>
              <el-switch v-model="row.is_active" size="small" />
            </span>
            <el-divider direction="vertical" />
          </div>
        </template>
      </el-table-column>

      <template #footer-batch-actions>
        <el-button type="primary" plain>设置角色</el-button>
        <el-button type="danger" plain @click="handleBatchDelete">删除</el-button>
      </template>
    </MkTable>

    <UserFromDrawer ref="userFormDrawerRef" />
  </div>
</template>

<style scoped lang="scss"></style>
