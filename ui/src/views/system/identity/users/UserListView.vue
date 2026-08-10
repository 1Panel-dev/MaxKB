<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '@/stores'
import UserManageApi from '@/api/admin/system/user-manage'
import type { LoginMethod, OptionItem, SystemUser, RequestParams } from '@/api/types/index.ts'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import { LOGIN_METHOD_LABELS } from '@/constants/auth.ts'
import MkWorkspaceRelationTags from '@/components/mk-workspace-relation-tags/index.vue'
import UserFromDrawer from './UserFromDrawer.vue'
import UserPwdDialog from './dialog/UserPwdDialog.vue'
import BatchSetUserRoleDialog from './dialog/BatchSetUserRoleDialog.vue'

const { auth, user } = useStore()
const route = useRoute()

/* 添加编辑用户表单drawer */
const userFormDrawerRef = ref<InstanceType<typeof UserFromDrawer>>()

/* 列表查询相关 */
const userTableRef = useTemplateRef('userTableRef')
const systemUsersLoading = ref(false)
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})
const systemUsersData = ref<SystemUser[]>([])
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
const systemUserQuery = ref<RequestParams>()

function handleSearchChange(query?: RequestParams) {
  systemUserQuery.value = query
  paginationConfig.value.currentPage = 1
  loadSystemUsers()
}

function loadSystemUsers(resetQuery = false) {
  systemUsersLoading.value = true
  if (resetQuery) {
    systemUserQuery.value = undefined
    paginationConfig.value.currentPage = 1
  }
  return UserManageApi.getUserManagePage(paginationConfig.value, systemUserQuery.value)
    .then((res) => {
      systemUsersData.value = res.records
      paginationConfig.value.total = res.total
    })
    .finally(() => {
      systemUsersLoading.value = false
    })
}

/* 密码修改dialog */
const userPwdDialogRef = ref<InstanceType<typeof UserPwdDialog>>()

/* 修改用户状态 */
function handleChangeStatus(systemUser: SystemUser) {
  const nextActive = !systemUser.is_active

  return UserManageApi.putUser(systemUser.id, {
    is_active: nextActive,
  })
    .then(() => {
      MsgSuccess(nextActive ? '启用成功' : '禁用成功')
      return true
    })
    .catch(() => false)
}

/* 删除用户*/
function deleteUser(user: SystemUser) {
  MsgConfirm(
    `确定删除用户“${user.username}”吗？`,
    '删除用户，该用户创建的资源（智能体、知识库、模型）不会删除，请谨慎操作。',
  )
    .then(() => {
      systemUsersLoading.value = true
      return UserManageApi.deleteUser(user.id).then(() => {
        MsgSuccess('删除成功')
        return loadSystemUsers()
      })
    })
    .catch(() => {})
    .finally(() => {
      systemUsersLoading.value = false
    })
}

/* 批量删除 */
const batchSelectedUsers = ref<SystemUser[]>([])
function handleBatchSelectionChange(selection: unknown[]) {
  batchSelectedUsers.value = selection as SystemUser[]
}
function handleBatchDelete() {
  const selectedUserIds = batchSelectedUsers.value.map(({ id }) => id)
  MsgConfirm(`是否删除选中的 ${batchSelectedUsers.value.length} 个用户？`)
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

/* 批量设置角色 */
const batchSetUserRoleDialogRef = ref<InstanceType<typeof BatchSetUserRoleDialog>>()
function openBatchSetUserRoleDialog() {
  batchSetUserRoleDialogRef.value?.open(batchSelectedUsers.value.map(({ id }) => id))
}

onMounted(() => loadSystemUsers())
</script>

<template>
  <div class="system-identity-users px-6">
    <header class="flex-between py-4">
      <h4>{{ route.meta.title }}</h4>
      <div class="flex items-center">
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
        <el-button class="ml-3">
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
      @current-change="loadSystemUsers()"
      @size-change="loadSystemUsers()"
      @selection-change="handleBatchSelectionChange"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="nick_name" label="姓名" min-width="150" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" min-width="150" show-overflow-tooltip />
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

      <el-table-column v-if="auth.isEE || auth.isPE" prop="role_name" width="180" label="角色">
        <template #default="{ row }">
          <MkWorkspaceRelationTags
            :table-render-params="{ property: '角色', value: '工作空间' }"
            :tags="row.role_name"
            :tag-workspace="row.role_workspace"
          />
        </template>
      </el-table-column>

      <el-table-column prop="user_group_names" width="180" label="用户组">
        <template #default="{ row }">
          <MkWorkspaceRelationTags
            :table-render-params="{ property: '用户组', value: '工作空间' }"
            :tags="row.role_name"
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
              <el-switch
                v-model="row.is_active"
                :disabled="row.role === 'ADMIN' || row.id === user.userInfo?.id"
                :before-change="() => handleChangeStatus(row)"
                size="small"
              />
            </span>
            <el-divider direction="vertical" />
            <div class="flex gap-1">
              <el-tooltip content="编辑" placement="top">
                <el-button type="primary" text @click.stop="userFormDrawerRef?.open(row)">
                  <mk-icon name="icon_edit_outlined"></mk-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="修改用户密码" placement="top">
                <el-button type="primary" text @click.stop="userPwdDialogRef?.open(row)">
                  <mk-icon name="icon-key_outlined"></mk-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button type="primary" text @click.stop="deleteUser(row)">
                  <mk-icon name="icon_delete-trash_outlined"></mk-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </template>
      </el-table-column>

      <template #footer-batch-actions>
        <el-button
          v-if="auth.isEE || auth.isPE"
          type="primary"
          plain
          @click="openBatchSetUserRoleDialog"
        >
          设置角色
        </el-button>
        <el-button type="danger" plain @click="handleBatchDelete">删除</el-button>
      </template>
    </MkTable>

    <UserFromDrawer ref="userFormDrawerRef" @refresh="loadSystemUsers" />
    <UserPwdDialog ref="userPwdDialogRef" @refresh="loadSystemUsers(false)" />
    <BatchSetUserRoleDialog ref="batchSetUserRoleDialogRef" @refresh="loadSystemUsers(false)" />
  </div>
</template>

<style scoped lang="scss"></style>
