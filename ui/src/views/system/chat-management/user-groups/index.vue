<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatUserGroupMember, Dict, ListItem, LoginMethod, OptionItem } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'
import ChatGroupsApi from '@/api/admin/system/chat-management/chat-user-groups.ts'
import CreateGroupMemberDialog from './dialog/CreateGroupMemberDialog.vue'
import CreateOrUpdateGroupDialog from './dialog/CreateOrUpdateGroupDialog.vue'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })

/* 添加用户组表单dialog */
const groupDialogRef = useTemplateRef<InstanceType<typeof CreateOrUpdateGroupDialog>>('groupDialogRef')

function handleOpenGroupDialog(group?: ListItem) {
  groupDialogRef.value?.open(group)
}

/* 用户组列表与选择 */
const groupsLoading = ref(false)
const chatUserGroups = ref<ListItem[]>([])
const currentGroup = ref<ListItem>()
function loadChatUserGroups(preferredGroupId?: string) {
  groupsLoading.value = true
  return ChatGroupsApi.getChatUserGroups()
    .then((groups) => {
      chatUserGroups.value = groups
      const selectedGroupId = preferredGroupId ?? currentGroup.value?.id
      currentGroup.value = groups.find(({ id }) => id === selectedGroupId) ?? groups[0]
      if (currentGroup.value) return loadGroupMembers(true)
      groupMembers.value = []
      paginationConfig.value.total = 0
    })
    .finally(() => {
      groupsLoading.value = false
    })
}

function handleGroupSelect(group: ListItem) {
  if (currentGroup.value?.id === group.id) return
  currentGroup.value = group
  loadGroupMembers(true)
}

/* 删除用户组 */
function deleteGroup(group: ListItem) {
  MsgConfirm(t('userGroup.delete.title', { name: group.name }), t('userGroup.delete.chatDescription'))
    .then(() => {
      groupsLoading.value = true
      return ChatGroupsApi.deleteChatUserGroup(group.id).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
        return loadChatUserGroups()
      })
    })
    .catch(() => {})
    .finally(() => {
      groupsLoading.value = false
    })
}

/* 用户组成员列表 */

const memberTableRef = useTemplateRef('memberTableRef')
const membersLoading = ref(false)
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const memberQuery = ref<Dict<unknown>>()
const memberSearchFields = computed<OptionItem<string>[]>(() => [
  { label: t('user.name.label'), value: 'nick_name' },
  { label: t('user.username.label'), value: 'username' },
])

/* 表头筛选 */
const selectedMemberSource = ref<string | null>(null)
const memberSourceLabels = computed<Record<LoginMethod, string>>(() => ({
  ...LOGIN_METHOD_LABELS,
  [LOGIN_METHOD.LOCAL]: t('user.source.local'),
}))
const memberSourceOptions = computed<OptionItem<string>[]>(() => Object.entries(memberSourceLabels.value).map(([value, label]) => ({ label, value })))
const memberListQuery = computed<Dict<unknown>>(() => ({
  ...memberQuery.value,
  ...(selectedMemberSource.value !== null ? { source: selectedMemberSource.value } : {}),
}))

const groupMembers = ref<ChatUserGroupMember[]>([])

function loadGroupMembers(resetPage = false) {
  const groupId = currentGroup.value?.id
  if (!groupId) return Promise.resolve()
  if (resetPage) paginationConfig.value.currentPage = 1

  membersLoading.value = true
  return ChatGroupsApi.getChatUserGroupMembers(groupId, paginationConfig.value, memberListQuery.value)
    .then((page) => {
      groupMembers.value = page.records
      paginationConfig.value.total = page.total
    })
    .finally(() => {
      membersLoading.value = false
    })
}

function handleMemberSearch(query?: Dict<unknown>) {
  memberQuery.value = query
  loadGroupMembers(true)
}

function handleMemberFilterChange() {
  loadGroupMembers(true)
}

/* 添加成员drawer */
const memberDialogRef = useTemplateRef<InstanceType<typeof CreateGroupMemberDialog>>('memberDialogRef')

function handleOpenMemberDialog() {
  memberDialogRef.value?.open()
}

/* (批量)移除成员 */
const batchSelectedMembers = ref<ChatUserGroupMember[]>([])
function handleBatchSelectionChange(selection: unknown[]) {
  batchSelectedMembers.value = selection as ChatUserGroupMember[]
}

function handleRemoveMembers(member?: ChatUserGroupMember) {
  const group = currentGroup.value
  const members = member ? [member] : batchSelectedMembers.value
  if (!group || !members.length) return

  const targetName = member ? member.nick_name || member.username : ''
  const title = member
    ? t('system.member.removeTitle', { name: targetName })
    : t('system.member.batchRemoveTitle', { count: members.length }, members.length)
  MsgConfirm(title, t('userGroup.delete.removeDescription'), { confirmButtonText: t('common.actions.remove') })
    .then(() => {
      membersLoading.value = true
      const relationIds = members.map(({ user_group_relation_id }) => user_group_relation_id)
      return ChatGroupsApi.postRemoveChatUserGroupMembers(group.id, relationIds).then(async () => {
        MsgSuccess(t('common.messages.removeSuccess'))
        await loadGroupMembers()
        memberTableRef.value?.clearSelection()
      })
    })
    .catch(() => {})
    .finally(() => {
      membersLoading.value = false
    })
}

onMounted(() => loadChatUserGroups())
</script>

<template>
  <MkViewLayout class="system-chat-groups" :title="t('system.menu.chatUserGroup')" :loading="groupsLoading">
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <!-- 创建用户组 -->
        <MkTooltip :content="t('userGroup.createTitle')" placement="top" v-if="perm.system.chatUserGroup.create()">
          <el-button text type="primary" @click="handleOpenGroupDialog()">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>
      <MkSearchList :data="chatUserGroups" :default-active="currentGroup?.id" @click="handleGroupSelect">
        <template #action-dropdown="{ row }">
          <!-- 重命名用户组 -->
          <MkDropdownItem v-if="perm.system.chatUserGroup.edit()" @click="handleOpenGroupDialog(row)">
            <template #icon><MkIcon name="icon_rename_outlined" /></template>
            <span>{{ t('common.actions.rename') }}</span>
          </MkDropdownItem>
          <!-- 删除用户组 -->
          <MkDropdownItem v-if="perm.system.chatUserGroup.delete()" @click="deleteGroup(row)">
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
            <span>{{ t('common.actions.delete') }}</span>
          </MkDropdownItem>
        </template>
      </MkSearchList>
    </template>
    <template #default="{ Header }">
      <template v-if="currentGroup">
        <component :is="Header">
          <div class="flex-align-center min-w-0 flex-1 gap-2">
            <h4 class="min-w-0 truncate" :title="currentGroup.name">{{ currentGroup.name }}</h4>
            <el-divider direction="vertical" />
            <span class="flex-align-center text-N500">
              <MkIcon name="icon_member_filled" class="mr-1" />
              {{ paginationConfig.total }}
            </span>
          </div>
        </component>

        <div class="flex-between mb-4">
          <div>
            <!-- 添加成员 -->
            <el-button v-if="perm.system.chatUserGroup.addMember()" type="primary" @click="handleOpenMemberDialog">
              <MkIcon name="icon_add_outlined" />
              <span>{{ t('system.member.add') }}</span>
            </el-button>
          </div>

          <MkComplexSearch :fields="memberSearchFields" @change="handleMemberSearch" />
        </div>

        <MkTable
          ref="memberTableRef"
          v-model:pagination-config="paginationConfig"
          :data="groupMembers"
          v-loading="membersLoading"
          @current-change="loadGroupMembers()"
          @size-change="loadGroupMembers()"
          @selection-change="handleBatchSelectionChange"
          :max-table-height="280"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column prop="nick_name" :label="t('user.name.label')" show-overflow-tooltip />
          <el-table-column prop="username" :label="t('user.username.label')" show-overflow-tooltip />
          <el-table-column prop="source" :label="t('user.source.label')">
            <template #header>
              <MkTableFilter
                mode="single"
                v-model="selectedMemberSource"
                :label="t('user.source.label')"
                :options="memberSourceOptions"
                @change="handleMemberFilterChange"
              />
            </template>
            <template #default="{ row }">
              {{ memberSourceLabels[row.source as LoginMethod] ?? row.source }}
            </template>
          </el-table-column>
          <el-table-column :label="t('common.labels.operation')" width="80" fixed="right">
            <template #default="{ row }">
              <!-- 移除成员 -->
              <MkTooltip :content="t('common.actions.remove')" placement="top" v-if="perm.system.chatUserGroup.removeMember()">
                <el-button type="primary" text @click="handleRemoveMembers(row)">
                  <MkIcon name="icon_assigned_outlined" />
                </el-button>
              </MkTooltip>
            </template>
          </el-table-column>
          <template #footer-batch-actions>
            <!-- 批量移除成员 -->
            <el-button v-if="perm.system.chatUserGroup.removeMember()" type="danger" plain @click="handleRemoveMembers()">
              {{ t('common.actions.remove') }}
            </el-button>
          </template>
        </MkTable>
      </template>
      <MkEmpty v-else class="flex-1" />
    </template>
  </MkViewLayout>

  <CreateOrUpdateGroupDialog ref="groupDialogRef" @refresh="loadChatUserGroups" />
  <CreateGroupMemberDialog ref="memberDialogRef" :current-group="currentGroup" @refresh="loadGroupMembers(true)" />
</template>
