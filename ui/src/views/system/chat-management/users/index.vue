<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import ChatUserApi from '@/api/admin/system/chat-management/chat-user.ts'
import type { ChatUser, Dict, LoginMethod, OptionItem } from '@/api/types'
import { LOGIN_METHOD, QUOTA_TYPE } from '@/api/enums'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { datetimeFormat } from '@/utils/time'
import { toOrderBy } from '@/utils/common'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { formatTokenNumber } from '@/utils/number'
import UserFromDrawer from './UserFromDrawer.vue'
import ButtonImportUsers from './import-users/ButtonImportUsers.vue'
import ButtonChangeUserPassword from './user-password/ButtonChangeUserPassword.vue'
import ButtonBatchSetUserGroup from './batch-set-user-group/ButtonBatchSetUserGroup.vue'
import ButtonQuotaSettings from './quota-settings/ButtonQuotaSettings.vue'
import perm from '@/permission/index.ts'

/* 添加编辑用户表单drawer */
const userFormDrawerRef = ref<InstanceType<typeof UserFromDrawer>>()

function handleOpenUserFormDrawer(chatUser?: ChatUser) {
  userFormDrawerRef.value?.open(chatUser)
}

/* 列表查询相关 */
const userTableRef = useTemplateRef('userTableRef')
const chatUsersLoading = ref(false)
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const chatUsersData = ref<ChatUser[]>([])
const orderBy = ref<string>()
const searchFields: OptionItem<string>[] = [
  { label: '姓名', value: 'nick_name' },
  { label: '用户名', value: 'username' },
  { label: '邮箱', value: 'email' },
]
const chatUserSearchQuery = ref<Dict<unknown>>()

/* 表头筛选 */
const selectedStatus = ref<boolean | null>(null)
const statusOptions: OptionItem<boolean>[] = [
  { label: '已启用', value: true },
  { label: '已禁用', value: false },
]
const selectedSource = ref<string | null>(null)
const sourceOptions: OptionItem<string>[] = Object.entries(LOGIN_METHOD_LABELS).map(([value, label]) => ({
  label: value === LOGIN_METHOD.LOCAL ? '本地创建' : label,
  value,
}))
const chatUserQuery = computed<Dict<unknown>>(() => ({
  ...chatUserSearchQuery.value,
  order_by: orderBy.value,
  ...(selectedStatus.value !== null ? { is_active: selectedStatus.value } : {}),
  ...(selectedSource.value !== null ? { source: selectedSource.value } : {}),
}))

function formatQuotaUsage(tokenQuota?: ChatUser['token_quota']) {
  if (!tokenQuota) return '-'
  const used = formatTokenNumber(tokenQuota.used_tokens)
  if (tokenQuota.quota_type === QUOTA_TYPE.UNLIMITED) return `${used} / 不限`
  return `${used} / ${formatTokenNumber(tokenQuota.token_limit)}`
}

function handleSearchChange(query?: Dict<unknown>) {
  chatUserSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  loadChatUsers()
}

function handleFilterChange() {
  paginationConfig.value.currentPage = 1
  return loadChatUsers()
}

/* 表头排序：清空选择并重新查询第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort, (prop) => (prop === 'token_quota.used_tokens' ? 'used_tokens' : prop))
  userTableRef.value?.clearSelection()
  return handleFilterChange()
}

function loadChatUsers(resetQuery = false) {
  chatUsersLoading.value = true
  if (resetQuery) {
    chatUserSearchQuery.value = undefined
    paginationConfig.value.currentPage = 1
  }
  return ChatUserApi.getChatUserPage(paginationConfig.value, chatUserQuery.value)
    .then((res) => {
      chatUsersData.value = res.records
      paginationConfig.value.total = res.total
    })
    .finally(() => {
      chatUsersLoading.value = false
    })
}

/* 修改用户状态 */
function handleChangeStatus(user: ChatUser) {
  const nextActive = !user.is_active

  return ChatUserApi.putChatUser(user.id, { is_active: nextActive })
    .then(() => {
      MsgSuccess(nextActive ? '启用成功' : '禁用成功')
      return true
    })
    .catch(() => false)
}

/* 删除用户 */
function deleteUser(user: ChatUser) {
  MsgConfirm(`确定删除用户：${user.username}？`)
    .then(() => {
      chatUsersLoading.value = true
      return ChatUserApi.deleteChatUser(user.id).then(() => {
        MsgSuccess('删除成功')
        return loadChatUsers()
      })
    })
    .catch(() => {})
    .finally(() => {
      chatUsersLoading.value = false
    })
}

/* 批量删除 */
const batchSelectedUsers = ref<ChatUser[]>([])

function handleBatchSelectionChange(selection: unknown[]) {
  batchSelectedUsers.value = selection as ChatUser[]
}

function handleBatchDelete() {
  const selectedUserIds = batchSelectedUsers.value.map(({ id }) => id)
  MsgConfirm(`是否删除选中的 ${batchSelectedUsers.value.length} 个用户？`)
    .then(() => {
      chatUsersLoading.value = true

      return ChatUserApi.postBatchDeleteChatUsers(selectedUserIds).then(async () => {
        MsgSuccess('删除成功')
        await loadChatUsers()
        userTableRef.value?.clearSelection()
      })
    })
    .catch(() => {})
    .finally(() => {
      chatUsersLoading.value = false
    })
}

onMounted(() => loadChatUsers())
</script>

<template>
  <MkViewLayout class="system-chat-users" :loading="chatUsersLoading">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex-align-center">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 导入用户 -->
          <ButtonImportUsers v-if="perm.system.chatUser.sync()" @refresh="loadChatUsers(true)" />
          <!-- 创建用户 -->
          <el-button v-if="perm.system.chatUser.create()" type="primary" @click="handleOpenUserFormDrawer()">
            <MkIcon name="icon_add_outlined" />
            <span>创建用户</span>
          </el-button>
        </div>
      </component>

      <MkTable
        ref="userTableRef"
        v-model:pagination-config="paginationConfig"
        :data="chatUsersData"
        v-loading="chatUsersLoading"
        @current-change="loadChatUsers()"
        @size-change="loadChatUsers()"
        @selection-change="handleBatchSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column type="selection" width="40" />
        <el-table-column prop="nick_name" label="姓名" min-width="150" show-overflow-tooltip />
        <el-table-column prop="username" label="用户名" min-width="150" show-overflow-tooltip />
        <el-table-column width="100" label="状态">
          <template #header>
            <MkTableFilter mode="single" v-model="selectedStatus" label="状态" :options="statusOptions" @change="handleFilterChange" />
          </template>
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

        <el-table-column prop="user_group_names" width="180" label="用户组">
          <template #default="{ row }">
            <MkTagGroup v-if="row.user_group_names?.length" :tags="row.user_group_names" />
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="用户来源" width="120">
          <template #header>
            <MkTableFilter mode="single" v-model="selectedSource" label="用户来源" :options="sourceOptions" @change="handleFilterChange" />
          </template>
          <template #default="{ row }">
            {{ row.source === LOGIN_METHOD.LOCAL ? '本地创建' : LOGIN_METHOD_LABELS[row.source as LoginMethod] }}
          </template>
        </el-table-column>

        <el-table-column prop="token_quota.used_tokens" label="Tokens使用量/总量" width="180" min-width="170" sortable>
          <template #default="{ row }">
            {{ formatQuotaUsage(row.token_quota) }}
          </template>
        </el-table-column>

        <el-table-column label="Tokens到期时间" min-width="180">
          <template #default="{ row }">
            {{ row.token_quota?.period_end ? datetimeFormat(row.token_quota?.period_end) : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="create_time" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- 修改状态 -->
              <el-switch
                v-model="row.is_active"
                size="small"
                :disabled="!perm.system.chatUser.edit()"
                :before-change="() => handleChangeStatus(row)"
              />
              <el-divider direction="vertical" class="ml-3! mr-2!" />

              <div class="flex">
                <!-- 编辑 -->
                <MkTooltip content="编辑" placement="top" v-if="perm.system.chatUser.edit()">
                  <el-button type="primary" text @click.stop="handleOpenUserFormDrawer(row)">
                    <MkIcon name="icon_edit_outlined" />
                  </el-button>
                </MkTooltip>
                <!-- 修改用户密码 -->
                <ButtonChangeUserPassword :user="row" @refresh="loadChatUsers(false)" />
                <!-- 更多 -->
                <MkTableMoreDropdown>
                  <!-- 配额设置 -->
                  <ButtonQuotaSettings v-if="perm.system.chatUser.quotaSetting()" :user-ids="row.id" dropdown @refresh="loadChatUsers()" />
                  <!-- 删除 -->
                  <MkDropdownItem v-if="perm.system.chatUser.delete()" divided @click="deleteUser(row)">
                    <template #icon>
                      <MkIcon name="icon_delete-trash_outlined" />
                    </template>
                    <span>删除</span>
                  </MkDropdownItem>
                </MkTableMoreDropdown>
              </div>
            </div>
          </template>
        </el-table-column>

        <template #footer-batch-actions>
          <!-- 批量设置用户组 -->
          <ButtonBatchSetUserGroup
            v-if="perm.system.chatUser.userGroup()"
            :user-ids="batchSelectedUsers.map(({ id }) => id)"
            @refresh="loadChatUsers(false)"
          />
          <!-- 批量配额设置-->
          <ButtonQuotaSettings
            v-if="perm.system.chatUser.quotaSetting()"
            :user-ids="batchSelectedUsers.map(({ id }) => id)"
            @refresh="loadChatUsers()"
          />
          <!-- 批量删除-->
          <el-button v-if="perm.system.chatUser.delete()" type="danger" plain @click="handleBatchDelete">删除</el-button>
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <UserFromDrawer ref="userFormDrawerRef" @refresh="loadChatUsers" />
</template>
