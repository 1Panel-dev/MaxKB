<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import ChatUserApi from '@/api/admin/system/chat-user/chat-user'
import type { ChatUser, Dict, LoginMethod, OptionItem } from '@/api/types'
import { LOGIN_METHOD, QUOTA_TYPE } from '@/api/enums'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { formatTokenNumber } from '@/utils/number'
import UserFromDrawer from './UserFromDrawer.vue'
import ImportUsersButton from './import-users/ImportUsersButton.vue'
import UserPwdButton from './user-password/UserPwdButton.vue'
import BatchSetUserGroupButton from './batch-set-user-group/BatchSetUserGroupButton.vue'
import QuotaSettingsButton from './quota-settings/QuotaSettingsButton.vue'

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
const searchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
  {
    label: '状态',
    value: 'is_active',
    options: [
      { label: '启用', value: true },
      { label: '禁用', value: false },
    ],
  },
  {
    label: '用户来源',
    value: 'source',
    options: Object.entries(LOGIN_METHOD_LABELS).map(([value, label]) => ({ label: value === LOGIN_METHOD.LOCAL ? '本地创建' : label, value })),
  },
]
const chatUserQuery = ref<Dict<unknown>>()

function formatQuotaUsage(tokenQuota?: ChatUser['token_quota']) {
  if (!tokenQuota) return '-'
  const used = formatTokenNumber(tokenQuota.used_tokens)
  if (tokenQuota.quota_type === QUOTA_TYPE.UNLIMITED) return `${used} / 不限`
  return `${used} / ${formatTokenNumber(tokenQuota.token_limit)}`
}

function handleSearchChange(query?: Dict<unknown>) {
  chatUserQuery.value = query
  paginationConfig.value.currentPage = 1
  loadChatUsers()
}

function loadChatUsers(resetQuery = false) {
  chatUsersLoading.value = true
  if (resetQuery) {
    chatUserQuery.value = undefined
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
        <div class="flex items-center">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 导入用户 -->
          <ImportUsersButton @refresh="loadChatUsers(true)" />
          <!-- 创建用户 -->
          <el-button type="primary" @click="handleOpenUserFormDrawer()">
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

        <el-table-column prop="user_group_names" width="180" label="用户组">
          <template #default="{ row }">
            <MkTagGroup :tags="row.user_group_names" />
          </template>
        </el-table-column>

        <el-table-column label="用户来源" width="120">
          <template #default="{ row }">
            {{ row.source === LOGIN_METHOD.LOCAL ? '本地创建' : LOGIN_METHOD_LABELS[row.source as LoginMethod] }}
          </template>
        </el-table-column>

        <el-table-column label="Tokens使用量/总量" min-width="150">
          <template #default="{ row }">
            {{ formatQuotaUsage(row.token_quota) }}
          </template>
        </el-table-column>

        <el-table-column label="Tokens到期时间" min-width="180">
          <template #default="{ row }">
            {{ row.token_quota?.period_end ? datetimeFormat(row.token_quota?.period_end) : '-' }}
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
                <el-switch v-model="row.is_active" size="small" :before-change="() => handleChangeStatus(row)" />
              </span>
              <el-divider direction="vertical" />
              <div class="flex">
                <!-- 编辑 -->
                <el-tooltip content="编辑" placement="top">
                  <el-button type="primary" text @click.stop="handleOpenUserFormDrawer(row)">
                    <MkIcon name="icon_edit_outlined" />
                  </el-button>
                </el-tooltip>
                <!-- 修改用户密码 -->
                <UserPwdButton :user="row" @refresh="loadChatUsers(false)" />
                <!-- 更多 -->
                <MkTableMoreDropdown class="ml-1" persistent>
                  <!-- 配额设置 -->
                  <QuotaSettingsButton :user-ids="row.id" dropdown @refresh="loadChatUsers()" />
                  <!-- 删除 -->
                  <MkDropdownItem divided @click="deleteUser(row)">
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
          <BatchSetUserGroupButton :user-ids="batchSelectedUsers.map(({ id }) => id)" @refresh="loadChatUsers(false)" />
          <!-- 批量配额设置-->
          <QuotaSettingsButton :user-ids="batchSelectedUsers.map(({ id }) => id)" @refresh="loadChatUsers()" />
          <!-- 批量删除-->
          <el-button type="danger" plain @click="handleBatchDelete">删除</el-button>
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <UserFromDrawer ref="userFormDrawerRef" @refresh="loadChatUsers" />
</template>
