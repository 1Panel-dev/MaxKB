<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import ChatGroupsApi from '@/api/admin/system/chat-management/chat-user-groups.ts'
import { LOGIN_METHOD } from '@/api/enums'
import type { ListItem, ChatUserGroupMember, LoginMethod, OptionItem, Dict } from '@/api/types'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import MkSearchList from '@/components/mk-search-list/index.vue'
import CreateGroupMemberDialog from './dialog/CreateGroupMemberDialog.vue'
import CreateOrUpdateGroupDialog from './dialog/CreateOrUpdateGroupDialog.vue'
import perm from '@/permission/index.ts'

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
  MsgConfirm(`确定删除用户组“${group.name}”吗？`, '删除后，组内成员不会被删除。')
    .then(() => {
      groupsLoading.value = true
      return ChatGroupsApi.deleteChatUserGroup(group.id).then(() => {
        MsgSuccess('删除成功')
        if (currentGroup.value?.id === group.id) {
          return loadChatUserGroups()
        }
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
const memberSearchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
  { label: '用户来源', value: 'source' },
]

const groupMembers = ref<ChatUserGroupMember[]>([])

function loadGroupMembers(resetPage = false) {
  const groupId = currentGroup.value?.id
  if (!groupId) return Promise.resolve()
  if (resetPage) paginationConfig.value.currentPage = 1

  membersLoading.value = true
  return ChatGroupsApi.getChatUserGroupMembers(groupId, paginationConfig.value, memberQuery.value)
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
  const title = member ? `是否移除成员：${member?.nick_name}？` : `是否移除选中的 ${batchSelectedMembers.value.length} 个成员？`
  MsgConfirm(title, '', { confirmButtonText: '移除' })
    .then(() => {
      membersLoading.value = true
      const relationIds = batchSelectedMembers.value.map(({ user_group_relation_id }) => user_group_relation_id)
      return ChatGroupsApi.postRemoveChatUserGroupMembers(currentGroup.value!.id, relationIds).then(async () => {
        MsgSuccess('移除成功')
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
  <MkViewLayout class="system-chat-groups" :loading="groupsLoading">
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <!-- 创建用户组 -->
        <MkTooltip content="创建用户组" placement="top" v-if="perm.system.chatUserGroup.create()">
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
            <span>重命名</span>
          </MkDropdownItem>
          <!-- 删除用户组 -->
          <MkDropdownItem v-if="perm.system.chatUserGroup.delete()" divided @click="deleteGroup(row)">
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
            <span>删除</span>
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
              <span>添加成员</span>
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
          <el-table-column prop="nick_name" label="姓名" show-overflow-tooltip />
          <el-table-column prop="username" label="用户名" show-overflow-tooltip />
          <el-table-column prop="source" label="用户来源">
            <template #default="{ row }">
              {{ row.source === LOGIN_METHOD.LOCAL ? '系统用户' : LOGIN_METHOD_LABELS[row.source as LoginMethod] }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="70" fixed="right">
            <template #default="{ row }">
              <!-- 移除成员 -->
              <MkTooltip content="移除" placement="top" v-if="perm.system.chatUserGroup.removeMember()">
                <el-button type="primary" text @click="handleRemoveMembers(row)">
                  <MkIcon name="icon_assigned_outlined" />
                </el-button>
              </MkTooltip>
            </template>
          </el-table-column>
          <template #footer-batch-actions>
            <!-- 批量移除成员 -->
            <el-button v-if="perm.system.chatUserGroup.removeMember()" type="danger" plain @click="handleRemoveMembers()">移除</el-button>
          </template>
        </MkTable>
      </template>
      <MkEmpty v-else class="flex-1" />
    </template>
  </MkViewLayout>

  <CreateOrUpdateGroupDialog ref="groupDialogRef" @refresh="loadChatUserGroups" />
  <CreateGroupMemberDialog ref="memberDialogRef" :current-group="currentGroup" @refresh="loadGroupMembers(true)" />
</template>
