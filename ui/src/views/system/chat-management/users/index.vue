<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatUser, Dict, LoginMethod, OptionItem } from '@/api/types'
import { LOGIN_METHOD, QUOTA_TYPE } from '@/api/enums'
import ChatUserApi from '@/api/admin/system/chat-management/chat-user.ts'
import UserFromDrawer from './UserFromDrawer.vue'
import ButtonBatchSetUserGroup from './batch-set-user-group/ButtonBatchSetUserGroup.vue'
import ButtonImportUsers from './import-users/ButtonImportUsers.vue'
import ButtonQuotaSettings from './quota-settings/ButtonQuotaSettings.vue'
import ButtonChangeUserPassword from './user-password/ButtonChangeUserPassword.vue'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { useStore } from '@/stores'
import { toOrderBy } from '@/utils/common'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { formatTokenNumber } from '@/utils/number'
import { datetimeFormat } from '@/utils/time'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

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
const searchFields = computed<OptionItem<string>[]>(() => [
  { label: t('user.name.label'), value: 'nick_name' },
  { label: t('user.username.label'), value: 'username' },
  { label: t('user.email.label'), value: 'email' },
])
const chatUserSearchQuery = ref<Dict<unknown>>()

/* 表头筛选 */
const selectedStatus = ref<boolean | null>(null)
const statusOptions = computed<OptionItem<boolean>[]>(() => [
  { label: t('common.status.enabled'), value: true },
  { label: t('common.status.disabled'), value: false },
])
const selectedSource = ref<string | null>(null)
const userSourceLabels = computed<Record<LoginMethod, string>>(() => ({
  ...LOGIN_METHOD_LABELS,
  [LOGIN_METHOD.LOCAL]: t('chatUser.source.local'),
}))
const sourceOptions = computed<OptionItem<string>[]>(() => Object.entries(userSourceLabels.value).map(([value, label]) => ({ label, value })))
const chatUserQuery = computed<Dict<unknown>>(() => ({
  ...chatUserSearchQuery.value,
  order_by: orderBy.value,
  ...(selectedStatus.value !== null ? { is_active: selectedStatus.value } : {}),
  ...(selectedSource.value !== null ? { source: selectedSource.value } : {}),
}))

function formatQuotaUsage(tokenQuota?: ChatUser['token_quota']) {
  if (!tokenQuota) return `0 / ${t('chatUser.quota.unlimited')}`
  const used = formatTokenNumber(tokenQuota.used_tokens)
  if (tokenQuota.quota_type === QUOTA_TYPE.UNLIMITED) return `${used} / ${t('chatUser.quota.unlimited')}`
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
      MsgSuccess(t(nextActive ? 'common.messages.enableSuccess' : 'common.messages.disableSuccess'))
      return true
    })
    .catch(() => false)
}

/* 删除用户 */
function deleteUser(user: ChatUser) {
  MsgConfirm(t('user.delete.title', { name: user.username }))
    .then(() => {
      chatUsersLoading.value = true
      return ChatUserApi.deleteChatUser(user.id).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
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
  MsgConfirm(t('user.delete.batchTitle', { count: selectedUserIds.length }, selectedUserIds.length))
    .then(() => {
      chatUsersLoading.value = true

      return ChatUserApi.postBatchDeleteChatUsers(selectedUserIds).then(async () => {
        MsgSuccess(t('common.messages.deleteSuccess'))
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
  <MkViewLayout class="system-chat-users" :title="t('chatUser.title')" :loading="chatUsersLoading">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 导入用户 -->
          <span v-if="perm.system.chatUser.sync()">
            <ButtonImportUsers @refresh="loadChatUsers(true)" />
          </span>

          <!-- 创建用户 -->
          <el-button v-if="perm.system.chatUser.create()" type="primary" @click="handleOpenUserFormDrawer()">
            <MkIcon name="icon_add_outlined" />
            <span>{{ t('user.createTitle') }}</span>
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
        <el-table-column prop="nick_name" :label="t('user.name.label')" min-width="150" show-overflow-tooltip />
        <el-table-column prop="username" :label="t('user.username.label')" min-width="150" show-overflow-tooltip />
        <el-table-column width="100">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedStatus"
              :label="t('common.status.label')"
              :options="statusOptions"
              @change="handleFilterChange"
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

        <el-table-column prop="user_group_names" width="180" :label="t('system.menu.chatUserGroup')">
          <template #default="{ row }">
            <MkTagGroup v-if="row.user_group_names?.length" :tags="row.user_group_names" />
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column v-if="auth.isEE || auth.isPE" :label="t('user.source.label')" width="120">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedSource"
              :label="t('user.source.label')"
              :options="sourceOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">
            {{ userSourceLabels[row.source as LoginMethod] ?? row.source }}
          </template>
        </el-table-column>

        <el-table-column v-if="auth.isEE || auth.isPE" prop="token_quota.used_tokens" :label="t('chatUser.quota.usage')" width="180" min-width="170" sortable>
          <template #default="{ row }">
            {{ formatQuotaUsage(row.token_quota) }}
          </template>
        </el-table-column>

        <el-table-column v-if="auth.isEE || auth.isPE" :label="t('chatUser.quota.expiresAt')" min-width="180">
          <template #default="{ row }">
            {{ row.token_quota?.period_end ? datetimeFormat(row.token_quota?.period_end) : '-' }}
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
                size="small"
                :disabled="!perm.system.chatUser.edit()"
                :before-change="() => handleChangeStatus(row)"
              />
              <el-divider direction="vertical" class="ml-3! mr-2!" />

              <div class="flex">
                <!-- 编辑 -->
                <MkTooltip :content="t('common.actions.edit')" placement="top" v-if="perm.system.chatUser.edit()">
                  <el-button type="primary" text @click.stop="handleOpenUserFormDrawer(row)">
                    <MkIcon name="icon_edit_outlined" />
                  </el-button>
                </MkTooltip>
                <!-- 修改用户密码 -->
                <ButtonChangeUserPassword v-if="perm.system.chatUser.edit()" :user="row" @refresh="loadChatUsers(false)" />
                <!-- 更多 -->
                <MkTableMoreDropdown>
                  <!-- 配额设置 -->
                  <ButtonQuotaSettings v-if="perm.system.chatUser.quotaSetting()" :user-ids="row.id" dropdown @refresh="loadChatUsers()" />
                  <!-- 删除 -->
                  <MkDropdownItem v-if="perm.system.chatUser.delete()" @click="deleteUser(row)">
                    <template #icon>
                      <MkIcon name="icon_delete-trash_outlined" />
                    </template>
                    <span>{{ t('common.actions.delete') }}</span>
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
          <el-button v-if="perm.system.chatUser.delete()" type="danger" plain @click="handleBatchDelete">{{ t('common.actions.delete') }}</el-button>
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <UserFromDrawer ref="userFormDrawerRef" @refresh="loadChatUsers" />
</template>
