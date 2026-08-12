<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import WorkspaceApi from '@/api/admin/system/workspace'
import UserGroupsApi from '@/api/admin/system/user-groups'
import type {
  RequestParams,
  OptionItem,
  WorkspaceItem,
  SystemUserGroup,
  SystemUserGroupMember,
} from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import MkWorkspaceDropdown from '@/components/mk-workspace-dropdown/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'
import MkWorkspaceRelationTags from '@/components/mk-workspace-relation-tags/index.vue'
import CreateOrUpdateGroupDialog from './dialog/CreateOrUpdateGroupDialog.vue'
import CreateGroupMemberDialog from './dialog/CreateGroupMemberDialog.vue'

/* 成员列表相关 */
const loadingMembers = ref(false)
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0,
})
const memberSearchQuery = ref<RequestParams>()
const memberSearchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
]
const userGroupMembers = ref<SystemUserGroupMember[]>([])
function handleMemberSearch(query?: RequestParams) {
  memberSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  loadUserGroupMembers()
}

const selectedGroupMembers = ref<SystemUserGroupMember[]>([])
function handleMemberSelectionChange(selection: unknown[]) {
  selectedGroupMembers.value = selection as SystemUserGroupMember[]
}

/* 添加成员drawer */
const memberDialogRef =
  useTemplateRef<InstanceType<typeof CreateGroupMemberDialog>>('memberDialogRef')

function handleOpenMemberDialog() {
  memberDialogRef.value?.open()
}

function handleRemoveMembers(member?: SystemUserGroupMember) {
  const group = currentGroup.value
  const members = member ? [member] : selectedGroupMembers.value
  if (!group || !members.length) return

  const targetName = member ? member.nick_name || member.username : ''
  const title = member
    ? `是否移除成员：${targetName}？`
    : `是否移除选中的 ${members.length} 个成员？`
  MsgConfirm(title, '', { confirmButtonText: '移除' })
    .then(() => {
      return UserGroupsApi.postRemoveSystemUserGroupMembers(
        selectedWorkspaceId.value,
        group.id,
        members.map(({ system_user_group_relation_id }) => system_user_group_relation_id),
      ).then(() => {
        MsgSuccess('移除成功')
        const removedRelationIds = new Set(
          members.map(({ system_user_group_relation_id }) => system_user_group_relation_id),
        )
        userGroupMembers.value = userGroupMembers.value.filter(
          ({ system_user_group_relation_id }) =>
            !removedRelationIds.has(system_user_group_relation_id),
        )
        paginationConfig.value.total = userGroupMembers.value.length
        selectedGroupMembers.value = []
        loadUserGroups()
      })
    })
    .catch(() => {})
}

/* 选择用户组列表 */
const loadingGroups = ref(false)
const currentGroup = ref<SystemUserGroup>()
const userGroups = ref<SystemUserGroup[]>([])

function loadUserGroups() {
  loadingGroups.value = true
  return UserGroupsApi.getSystemUserGroups(selectedWorkspaceId.value)
    .then((groups) => {
      userGroups.value = groups
      if (!currentGroup.value || !groups.some(({ id }) => id === currentGroup.value?.id)) {
        currentGroup.value = groups[0]
        loadUserGroupMembers()
      }
    })
    .finally(() => {
      loadingGroups.value = false
    })
}

function handleGroupSelect(group: SystemUserGroup) {
  currentGroup.value = group
  paginationConfig.value.currentPage = 1
  loadUserGroupMembers()
}

/* 新增、重命名用户组 */
const groupDialogRef =
  useTemplateRef<InstanceType<typeof CreateOrUpdateGroupDialog>>('groupDialogRef')

function handleOpenGroupDialog(group?: SystemUserGroup) {
  groupDialogRef.value?.open(group)
}

function handleGroupSaved(group: SystemUserGroup) {
  const existingIndex = userGroups.value.findIndex(({ id }) => id === group.id)
  if (existingIndex >= 0) {
    userGroups.value[existingIndex] = group
  } else {
    userGroups.value.push(group)
  }
  currentGroup.value = userGroups.value.find(({ id }) => id === group.id)
  if (currentGroup.value?.id === group.id) {
    loadUserGroupMembers()
  }
}

/* 删除用户组 */
function deleteGroup(group: SystemUserGroup) {
  MsgConfirm(`确定删除用户组"${group.name}"吗？`, '删除后，组内成员不会被删除。')
    .then(() => {
      return UserGroupsApi.deleteSystemUserGroup(selectedWorkspaceId.value, group.id).then(() => {
        MsgSuccess('删除成功')
        userGroups.value = userGroups.value.filter(({ id }) => id !== group.id)
        if (currentGroup.value?.id === group.id) {
          currentGroup.value = userGroups.value[0]
          loadUserGroupMembers()
        }
      })
    })
    .catch(() => {})
}

/* 加载成员列表 */
function loadUserGroupMembers(reset = false) {
  if (!currentGroup.value) return
  if (reset) {
    paginationConfig.value.currentPage = 1
  }

  const { currentPage, pageSize } = paginationConfig.value
  loadingMembers.value = true
  UserGroupsApi.getSystemUserGroupMembers(
    selectedWorkspaceId.value,
    currentGroup.value.id,
    { currentPage, pageSize },
    memberSearchQuery.value,
  )
    .then(({ total, records }) => {
      userGroupMembers.value = records
      paginationConfig.value.total = total
    })
    .finally(() => {
      loadingMembers.value = false
    })
}

/* 选择工作空间列表 */
const selectedWorkspaceId = ref('default')
const workspaceOptions = ref<WorkspaceItem[]>([])
const loadingView = ref(false)

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
  loadUserGroups()
}

function loadWorkspaceOptions() {
  loadingView.value = true
  return WorkspaceApi.getSystemWorkspaceList()
    .then((workspaces) => {
      workspaceOptions.value = workspaces

      if (!workspaceOptions.value.some(({ id }) => id === selectedWorkspaceId.value)) {
        selectedWorkspaceId.value = workspaceOptions.value[0]?.id ?? 'default'
      }

      return loadUserGroups()
    })
    .finally(() => {
      loadingView.value = false
    })
}

onMounted(() => loadWorkspaceOptions())
</script>

<template>
  <MkViewLayout class="system-identity-groups" :loading="loadingView">
    <template #top>
      <MkWorkspaceDropdown
        v-model="selectedWorkspaceId"
        :options="workspaceOptions"
        @select="handleWorkspaceSelect"
      />
    </template>
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <el-tooltip content="创建用户组" placement="top">
          <el-button class="-mr-1" text type="primary" @click="handleOpenGroupDialog()">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </el-tooltip>
      </component>
      <MkSearchList
        v-loading="loadingGroups"
        :data="userGroups"
        :default-active="currentGroup?.id"
        @click="handleGroupSelect"
      >
        <template #action-dropdown="{ row }">
          <MkDropdownMenu>
            <MkDropdownItem @click="handleOpenGroupDialog(row)">
              <template #icon>
                <MkIcon name="icon_edit_outlined" />
              </template>
              <span>重命名</span>
            </MkDropdownItem>
            <MkDropdownItem divided @click="deleteGroup(row)">
              <template #icon>
                <MkIcon name="icon_delete-trash_outlined" />
              </template>
              <span>删除</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkSearchList>
    </template>

    <template #default="{ Header }">
      <template v-if="currentGroup">
        <component :is="Header">
          <div class="flex items-center gap-2">
            <h4>{{ currentGroup.name }}</h4>
            <el-divider direction="vertical" />
            <span class="flex items-center text-N500">
              <MkIcon name="icon_member_filled" class="mr-1" />
              {{ currentGroup.count }}
            </span>
          </div>
        </component>

        <div class="flex-between mb-4">
          <el-button type="primary" @click="handleOpenMemberDialog">
            <MkIcon name="icon_add_outlined" />
            <span>添加成员</span>
          </el-button>
          <MkComplexSearch :fields="memberSearchFields" @change="handleMemberSearch" />
        </div>

        <MkTable
          v-loading="loadingMembers"
          :max-table-height="340"
          v-model:pagination-config="paginationConfig"
          :data="userGroupMembers"
          @selection-change="handleMemberSelectionChange"
          :search="Boolean(memberSearchQuery)"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column prop="nick_name" label="姓名" min-width="198" show-overflow-tooltip />
          <el-table-column prop="username" label="用户名" min-width="198" show-overflow-tooltip />
          <el-table-column label="角色" min-width="198">
            <template #default="{ row }">
              <MkWorkspaceRelationTags
                :table-render-params="{ property: '角色', value: '工作空间' }"
                :tags="row.role ? [row.role] : []"
              />
            </template>
          </el-table-column>
          <el-table-column prop="source" label="用户来源" min-width="198" show-overflow-tooltip />
          <el-table-column label="操作" width="70" fixed="right">
            <template #default="{ row }">
              <el-tooltip content="移除" placement="top">
                <el-button type="primary" text @click="handleRemoveMembers(row)">
                  <MkIcon name="icon_assigned_outlined" />
                </el-button>
              </el-tooltip>
            </template>
          </el-table-column>
          <template #footer-batch-actions>
            <el-button type="danger" plain @click="handleRemoveMembers()">移除</el-button>
          </template>
        </MkTable>
      </template>
      <MkEmpty v-else class="flex-1" />
    </template>
  </MkViewLayout>
  <CreateOrUpdateGroupDialog
    ref="groupDialogRef"
    :workspace-id="selectedWorkspaceId"
    @refresh="handleGroupSaved"
  />
  <CreateGroupMemberDialog
    ref="memberDialogRef"
    :workspace-id="selectedWorkspaceId"
    :current-group="currentGroup"
    @refresh="loadUserGroupMembers(true)"
  />
</template>
