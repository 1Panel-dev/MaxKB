<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, LoginMethod, OptionItem, SystemUser } from '@/api/types'
import { LOGIN_METHOD, ROLE_TYPE } from '@/api/enums'
import UserManageApi from '@/api/admin/system/user-manage'
import WorkspaceRelationTags from '@/components/business/workspace-relation-tags/index.vue'
import UserFromDrawer from './UserFromDrawer.vue'
import ButtonBatchSetUserRole from './batch-set-user-role/ButtonBatchSetUserRole.vue'
import ButtonImportUsers from './import-users/ButtonImportUsers.vue'
import ButtonChangeUserPassword from './user-password/ButtonChangeUserPassword.vue'
import { LOGIN_METHOD_LABELS } from '@/constants/auth.ts'
import { useStore } from '@/stores'
import { toOrderBy } from '@/utils/common'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })
const { auth, user } = useStore()

/* 添加编辑用户表单drawer */
const userFormDrawerRef = ref<InstanceType<typeof UserFromDrawer>>()

function handleOpenUserFormDrawer(systemUser?: SystemUser) {
  userFormDrawerRef.value?.open(systemUser)
}

/* 列表查询相关 */
const userTableRef = useTemplateRef('userTableRef')
const systemUsersLoading = ref(false)
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const systemUsersData = ref<SystemUser[]>([])
const orderBy = ref<string>()

const searchFields = computed<OptionItem<string>[]>(() => [
  { label: t('user.name.label'), value: 'nick_name' },
  { label: t('user.username.label'), value: 'username' },
  { label: t('user.email.label'), value: 'email' },
])
const systemUserSearchQuery = ref<Dict<unknown>>()
const userSourceLabels = computed<Record<LoginMethod, string>>(() => ({
  ...LOGIN_METHOD_LABELS,
  [LOGIN_METHOD.LOCAL]: t('user.source.local'),
  [LOGIN_METHOD.DINGTALK]: t('auth.login.options.dingtalk'),
  [LOGIN_METHOD.LARK]: t('auth.login.options.lark'),
  [LOGIN_METHOD.WECOM]: t('auth.login.options.wecom'),
}))
const sourceFilterOptions = computed<OptionItem<string>[]>(() => Object.entries(userSourceLabels.value).map(([value, label]) => ({ label, value })))
const selectedStatus = ref<boolean | null>(null)
const selectedSource = ref<string | null>(null)

const systemUserQuery = computed<Dict<unknown>>(() => ({
  ...systemUserSearchQuery.value,
  order_by: orderBy.value,
  ...(selectedStatus.value !== null ? { is_active: selectedStatus.value } : {}),
  ...(selectedSource.value !== null ? { source: selectedSource.value } : {}),
}))

function handleSearchChange(query?: Dict<unknown>) {
  systemUserSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  loadSystemUsers()
}

function handleHeaderFilterChange() {
  paginationConfig.value.currentPage = 1
  return loadSystemUsers()
}

/* 表头排序：清空选择并重新查询第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort)
  userTableRef.value?.clearSelection()
  return handleHeaderFilterChange()
}

function loadSystemUsers(resetQuery = false) {
  systemUsersLoading.value = true
  if (resetQuery) {
    systemUserSearchQuery.value = undefined
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

/* 修改用户状态 */
function handleChangeStatus(systemUser: SystemUser) {
  const nextActive = !systemUser.is_active

  return UserManageApi.putUser(systemUser.id, { is_active: nextActive })
    .then(() => {
      MsgSuccess(t(nextActive ? 'common.messages.enableSuccess' : 'common.messages.disableSuccess'))
      return true
    })
    .catch(() => false)
}

/* 删除用户*/
function deleteUser(user: SystemUser) {
  MsgConfirm(`${t('user.delete.title')}: ${user.username}?`, t('user.delete.description'))
    .then(() => {
      systemUsersLoading.value = true
      return UserManageApi.deleteUser(user.id).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
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
  MsgConfirm(`${t('user.delete.batchTitle', { count: batchSelectedUsers.value.length }, batchSelectedUsers.value.length)}?`)
    .then(() => {
      systemUsersLoading.value = true

      return UserManageApi.postBatchDeleteUsers(selectedUserIds).then(async () => {
        MsgSuccess(t('common.messages.deleteSuccess'))
        await loadSystemUsers()
        userTableRef.value?.clearSelection()
      })
    })

    .catch(() => {})
    .finally(() => {
      systemUsersLoading.value = false
    })
}

onMounted(() => loadSystemUsers())
</script>

<template>
  <MkViewLayout :title="t('user.title')" class="system-identity-users">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 导入用户 -->
          <span v-if="perm.system.user.import()">
            <ButtonImportUsers @refresh="loadSystemUsers()" />
          </span>

          <!-- 创建用户 -->
          <el-button v-if="perm.system.user.create()" type="primary" @click="handleOpenUserFormDrawer()">
            <MkIcon name="icon_add_outlined" />
            <span>{{ t('user.createTitle') }}</span>
          </el-button>
        </div>
      </component>

      <MkTable
        ref="userTableRef"
        v-model:pagination-config="paginationConfig"
        :data="systemUsersData"
        v-loading="systemUsersLoading"
        @current-change="loadSystemUsers()"
        @size-change="loadSystemUsers()"
        @selection-change="handleBatchSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column type="selection" width="40" />
        <el-table-column prop="nick_name" :label="t('user.name.label')" min-width="150" show-overflow-tooltip />
        <el-table-column prop="username" :label="t('user.username.label')" min-width="150" show-overflow-tooltip />
        <el-table-column width="140" :label="t('user.activeStatus')">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedStatus"
              :label="t('user.activeStatus')"
              :options="[
                { label: t('common.status.enabled'), value: true },
                { label: t('common.status.disabled'), value: false },
              ]"
              @change="handleHeaderFilterChange"
            />
          </template>
          <template #default="{ row }">
            <MkStatusLabel :active="row.is_active" />
          </template>
        </el-table-column>

        <el-table-column prop="email" :label="t('user.email.label')" show-overflow-tooltip min-width="180">
          <template #default="{ row }">
            {{ row.email || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" width="120" :label="t('user.phone.label')">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>

        <el-table-column v-if="auth.isEE || auth.isPE" prop="role_name" width="180" :label="t('user.role.label')">
          <template #default="{ row }">
            <span v-if="!row.role_workspace?.length">-</span>
            <WorkspaceRelationTags
              v-else
              :columns="[
                { prop: 'role_name', label: t('user.role.label') },
                { prop: 'workspace', label: t('workspace.title') },
              ]"
              :tags="row.role_name"
              :data="row.role_workspace"
            />
          </template>
        </el-table-column>

        <el-table-column prop="user_group_names" width="180" :label="t('userGroup.title')">
          <template #default="{ row }">
            <span v-if="!row.user_group_names?.length">-</span>
            <WorkspaceRelationTags
              v-else
              :columns="[
                { prop: 'user_group_names', label: t('userGroup.title') },
                { prop: 'workspace', label: t('workspace.title') },
              ]"
              :tags="row.user_group_names"
              :data="row.user_group_workspace ?? []"
            />
          </template>
        </el-table-column>

        <el-table-column width="120" :label="t('user.source.label')">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedSource"
              :label="t('user.source.label')"
              :options="sourceFilterOptions"
              @change="handleHeaderFilterChange"
            />
          </template>
          <template #default="{ row }">
            {{ userSourceLabels[row.source as LoginMethod] ?? row.source }}
          </template>
        </el-table-column>

        <el-table-column prop="create_time" :label="t('common.labels.createTime')" width="180" sortable>
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="t('common.labels.operation')" width="160" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- 修改状态 -->
              <el-switch
                v-model="row.is_active"
                :disabled="row.role === ROLE_TYPE.ADMIN || row.id === user.userInfo?.id || !perm.system.user.edit()"
                :before-change="() => handleChangeStatus(row)"
                size="small"
              />
              <el-divider direction="vertical" class="ml-3! mr-2!" />

              <div class="flex">
                <!-- 编辑 -->
                <MkTooltip :content="t('common.actions.edit')" placement="top" v-if="perm.system.user.edit()">
                  <el-button type="primary" text @click.stop="handleOpenUserFormDrawer(row)">
                    <MkIcon name="icon_edit_outlined" />
                  </el-button>
                </MkTooltip>
                <!-- 修改用户密码 -->
                <ButtonChangeUserPassword v-if="perm.system.user.edit()" :user="row" @refresh="loadSystemUsers(false)" />
                <!-- 删除 -->
                <MkTooltip :content="t('common.actions.delete')" placement="top" v-if="perm.system.user.delete()">
                  <el-button type="primary" :disabled="row.id === user.userInfo?.id" text @click.stop="deleteUser(row)">
                    <MkIcon name="icon_delete-trash_outlined" />
                  </el-button>
                </MkTooltip>
              </div>
            </div>
          </template>
        </el-table-column>

        <template #footer-batch-actions>
          <!-- 批量设置角色 -->
          <ButtonBatchSetUserRole
            v-if="(auth.isEE || auth.isPE) && perm.system.user.setRole()"
            :user-ids="batchSelectedUsers.map(({ id }) => id)"
            @refresh="loadSystemUsers(false)"
          />
          <!-- 批量删除 -->
          <el-button v-if="perm.system.user.delete()" type="danger" plain @click="handleBatchDelete">{{ t('common.actions.delete') }}</el-button>
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <UserFromDrawer ref="userFormDrawerRef" @refresh="loadSystemUsers" />
</template>

<style scoped lang="scss"></style>
