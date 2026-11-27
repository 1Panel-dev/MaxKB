<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, LoginMethod, OptionItem, RoleInfo, SystemUserGroup, SystemUserGroupMember, WorkspaceItem } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'
import UserGroupsApi from '@/api/admin/system/user-groups'
import WorkspaceApi from '@/api/admin/system/workspace'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import CreateGroupMemberDialog from './dialog/CreateGroupMemberDialog.vue'
import CreateOrUpdateGroupDialog from './dialog/CreateOrUpdateGroupDialog.vue'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { ADMIN_STORAGE_KEY } from '@/constants/storage-key'
import { useStore } from '@/stores'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { getRoleName } from '@/utils/role-name'
import perm from '@/permission/index.ts'
const { auth, user } = useStore()
const { t } = useI18n({ useScope: 'global' })

/* 选择工作空间列表 */
const selectedWorkspaceId = ref(localStorage.getItem(ADMIN_STORAGE_KEY.WORKSPACE_ID) || user.userInfo?.workspace_list?.[0]?.id || 'default')
const workspaceOptions = ref<WorkspaceItem[]>([])
const loadingView = ref(false)

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
  loadUserGroups()
}

function loadWorkspaceOptions() {
  return WorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
    workspaceOptions.value = workspaces
  })
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
const groupDialogRef = useTemplateRef<InstanceType<typeof CreateOrUpdateGroupDialog>>('groupDialogRef')

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
  MsgConfirm(t('userGroup.delete.title', { name: group.name }), t('userGroup.delete.description'))
    .then(() => {
      return UserGroupsApi.deleteSystemUserGroup(selectedWorkspaceId.value, group.id).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
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
  if (!currentGroup.value) return Promise.resolve()
  if (reset) {
    paginationConfig.value.currentPage = 1
  }

  const { currentPage, pageSize } = paginationConfig.value
  loadingMembers.value = true
  return UserGroupsApi.getSystemUserGroupMembers(selectedWorkspaceId.value, currentGroup.value.id, { currentPage, pageSize }, memberListQuery.value)
    .then(({ total, records }) => {
      userGroupMembers.value = records
      paginationConfig.value.total = total
    })
    .finally(() => {
      loadingMembers.value = false
    })
}

/* 成员列表相关 */
const loadingMembers = ref(false)
const memberTableRef = useTemplateRef('memberTableRef')
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const memberSearchQuery = ref<Dict<unknown>>()
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
  ...memberSearchQuery.value,
  ...(selectedMemberSource.value !== null ? { source: selectedMemberSource.value } : {}),
}))
const userGroupMembers = ref<SystemUserGroupMember[]>([])
function handleMemberSearch(query?: Dict<unknown>) {
  memberSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  loadUserGroupMembers()
}

function handleMemberFilterChange() {
  loadUserGroupMembers(true)
}

const selectedGroupMembers = ref<SystemUserGroupMember[]>([])
function handleMemberSelectionChange(selection: unknown[]) {
  selectedGroupMembers.value = selection as SystemUserGroupMember[]
}

/* 添加成员drawer */
const memberDialogRef = useTemplateRef<InstanceType<typeof CreateGroupMemberDialog>>('memberDialogRef')

function handleOpenMemberDialog() {
  memberDialogRef.value?.open()
}

function handleRemoveMembers(member?: SystemUserGroupMember) {
  const group = currentGroup.value
  const members = member ? [member] : selectedGroupMembers.value
  if (!group || !members.length) return

  const targetName = member ? member.nick_name || member.username : ''
  const title = member
    ? t('system.member.removeTitle', { name: targetName })
    : t('system.member.batchRemoveTitle', { count: members.length }, members.length)
  MsgConfirm(title, t('userGroup.delete.removeDescription'), { confirmButtonText: t('common.actions.remove') })
    .then(() => {
      loadingMembers.value = true
      return UserGroupsApi.postRemoveSystemUserGroupMembers(
        selectedWorkspaceId.value,
        group.id,
        members.map(({ system_user_group_relation_id }) => system_user_group_relation_id),
      ).then(async () => {
        MsgSuccess(t('common.messages.removeSuccess'))
        await loadUserGroupMembers()
        memberTableRef.value?.clearSelection()
        return loadUserGroups()
      })
    })
    .catch(() => {})
    .finally(() => {
      loadingMembers.value = false
    })
}

onMounted(() => {
  loadingView.value = true
  Promise.all(auth.isEE ? [loadWorkspaceOptions(), loadUserGroups()] : [loadUserGroups()]).finally(() => {
    loadingView.value = false
  })
})
</script>

<template>
  <MkViewLayout :title="t('userGroup.title')" class="system-identity-groups" :loading="loadingView">
    <template #top v-if="auth.isEE">
      <WorkspaceDropdown v-model="selectedWorkspaceId" :options="workspaceOptions" @select="handleWorkspaceSelect" />
    </template>
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <!-- 创建用户组 -->
        <MkTooltip v-if="perm.system.userGroup.create()" :content="t('userGroup.createTitle')" placement="top">
          <el-button class="-mr-1" text type="primary" @click="handleOpenGroupDialog()">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>
      <MkSearchList v-loading="loadingGroups" :data="userGroups" :default-active="currentGroup?.id" @click="handleGroupSelect">
        <template #action-dropdown="{ row }">
          <!-- 重命名用户组 -->
          <MkDropdownItem v-if="perm.system.userGroup.edit()" @click="handleOpenGroupDialog(row)">
            <template #icon>
              <MkIcon name="icon_rename_outlined" />
            </template>
            <span>{{ t('common.actions.rename') }}</span>
          </MkDropdownItem>
          <!-- 删除用户组 -->
          <MkDropdownItem v-if="perm.system.userGroup.delete()" @click="deleteGroup(row)">
            <template #icon>
              <MkIcon name="icon_delete-trash_outlined" />
            </template>
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
              {{ currentGroup.count }}
            </span>
          </div>
        </component>

        <div class="flex-between mb-4">
          <div>
            <!-- 添加成员 -->
            <el-button v-if="perm.system.userGroup.addMember()" type="primary" @click="handleOpenMemberDialog">
              <MkIcon name="icon_add_outlined" />
              <span>{{ t('system.member.add') }}</span>
            </el-button>
          </div>

          <MkComplexSearch :fields="memberSearchFields" @change="handleMemberSearch" />
        </div>

        <MkTable
          ref="memberTableRef"
          v-loading="loadingMembers"
          :max-table-height="280"
          v-model:pagination-config="paginationConfig"
          :data="userGroupMembers"
          @current-change="loadUserGroupMembers()"
          @size-change="loadUserGroupMembers()"
          @selection-change="handleMemberSelectionChange"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column prop="nick_name" :label="t('user.name.label')" min-width="198" show-overflow-tooltip />
          <el-table-column prop="username" :label="t('user.username.label')" min-width="198" show-overflow-tooltip />
          <el-table-column v-if="auth.isEE || auth.isPE" :label="t('user.role.label')" min-width="198">
            <template #default="{ row }">
              <MkTagGroup
                v-if="row.role_info?.length"
                :tags="row.role_info"
                :format-label="(role: RoleInfo) => getRoleName(role.role_id, role.role_name)"
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column v-if="auth.isEE || auth.isPE" prop="source" :label="t('user.source.label')" min-width="198" show-overflow-tooltip>
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
              <MkTooltip :content="t('common.actions.remove')" placement="top" v-if="perm.system.userGroup.removeMember()">
                <el-button type="primary" text @click="handleRemoveMembers(row)">
                  <MkIcon name="icon_assigned_outlined" />
                </el-button>
              </MkTooltip>
            </template>
          </el-table-column>
          <template #footer-batch-actions>
            <!-- 批量移除成员 -->
            <el-button v-if="perm.system.userGroup.removeMember()" type="danger" plain @click="handleRemoveMembers()">
              {{ t('common.actions.remove') }}
            </el-button>
          </template>
        </MkTable>
      </template>
      <MkEmpty v-else class="flex-1" />
    </template>
  </MkViewLayout>
  <CreateOrUpdateGroupDialog ref="groupDialogRef" :workspace-id="selectedWorkspaceId" @refresh="handleGroupSaved" />
  <CreateGroupMemberDialog
    ref="memberDialogRef"
    :workspace-id="selectedWorkspaceId"
    :current-group="currentGroup"
    @refresh="loadUserGroupMembers(true)"
  />
</template>
