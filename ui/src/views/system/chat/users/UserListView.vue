<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import ChatUserApi from '@/api/admin/system/chat-user'
import type { ChatUser, LoginMethod, OptionItem, RequestParams } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import UserFromDrawer from './UserFromDrawer.vue'
import ImportUsersDialog from './dialog/ImportUsersDialog.vue'
import UserPwdDialog from './dialog/UserPwdDialog.vue'
import BatchSetUserGroupDialog from './dialog/BatchSetUserGroupDialog.vue'

/* 添加编辑用户表单drawer */
const userFormDrawerRef = ref<InstanceType<typeof UserFromDrawer>>()

function handleOpenUserFormDrawer(chatUser?: ChatUser) {
  userFormDrawerRef.value?.open(chatUser)
}

/* 导入用户 */
const importUsersDialogRef = ref<InstanceType<typeof ImportUsersDialog>>()

function handleOpenImportUsersDialog() {
  importUsersDialogRef.value?.open()
}

/* 列表查询相关 */
const userTableRef = useTemplateRef('userTableRef')
const chatUsersLoading = ref(false)
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})
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
    options: Object.entries(LOGIN_METHOD_LABELS).map(([value, label]) => ({
      label: value === LOGIN_METHOD.LOCAL ? '本地创建' : label,
      value,
    })),
  },
]
const chatUserQuery = ref<RequestParams>()

function handleSearchChange(query?: RequestParams) {
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

/* 密码修改dialog */
const userPwdDialogRef = ref<InstanceType<typeof UserPwdDialog>>()

function handleOpenUserPwdDialog(chatUser: ChatUser) {
  userPwdDialogRef.value?.open(chatUser)
}

/* 修改用户状态 */
function handleChangeStatus(user: ChatUser) {
  const nextActive = !user.is_active

  return ChatUserApi.putChatUser(user.id, {
    is_active: nextActive,
  })
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

/* 批量设置用户组 */
const batchSetUserGroupDialogRef = ref<InstanceType<typeof BatchSetUserGroupDialog>>()

function openBatchSetUserGroupDialog() {
  batchSetUserGroupDialogRef.value?.open(batchSelectedUsers.value.map(({ id }) => id))
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
          <el-button class="ml-3" @click="handleOpenImportUsersDialog">
            <MkIcon name="icon_import_outlined" />
            <span>导入用户</span>
          </el-button>
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
        :isSearching="Boolean(chatUserQuery)"
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

        <el-table-column label="用户来源">
          <template #default="{ row }">
            {{
              row.source === LOGIN_METHOD.LOCAL
                ? '本地创建'
                : LOGIN_METHOD_LABELS[row.source as LoginMethod]
            }}
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
                  size="small"
                  :before-change="() => handleChangeStatus(row)"
                />
              </span>
              <el-divider direction="vertical" />
              <div class="flex gap-1">
                <el-tooltip content="编辑" placement="top">
                  <el-button type="primary" text @click.stop="handleOpenUserFormDrawer(row)">
                    <mk-icon name="icon_edit_outlined"></mk-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="修改用户密码" placement="top">
                  <el-button type="primary" text @click.stop="handleOpenUserPwdDialog(row)">
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
          <el-button type="primary" plain @click="openBatchSetUserGroupDialog">
            设置用户组
          </el-button>
          <el-button type="danger" plain @click="handleBatchDelete">删除</el-button>
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <UserFromDrawer ref="userFormDrawerRef" @refresh="loadChatUsers" />
  <ImportUsersDialog ref="importUsersDialogRef" @refresh="loadChatUsers(true)" />
  <UserPwdDialog ref="userPwdDialogRef" @refresh="loadChatUsers(false)" />
  <BatchSetUserGroupDialog ref="batchSetUserGroupDialogRef" @refresh="loadChatUsers(false)" />
</template>
