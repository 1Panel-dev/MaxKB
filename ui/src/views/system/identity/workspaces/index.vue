<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, OptionItem, WorkspaceItem, WorkspaceMemberItem } from '@/api/types'
import type { TableColumnCtx } from 'element-plus'
import WorkspaceApi from '@/api/admin/system/workspace'
import AddMemberDrawer from './AddMemberDrawer.vue'
import CreateOrUpdateWorkspaceDialog from './dialog/CreateOrUpdateWorkspaceDialog.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })

/* 添加工作空间表单dialog */
const workspaceDialogRef = useTemplateRef<InstanceType<typeof CreateOrUpdateWorkspaceDialog>>('workspaceDialogRef')

function handleOpenWorkspaceDialog(workspace?: WorkspaceItem) {
  workspaceDialogRef.value?.open(workspace)
}

/* 选择工作空间列表 */
const workspaceLoading = ref(false)
const currentWorkspace = ref<WorkspaceItem>()
const workspacesList = ref<WorkspaceItem[]>([])

function loadWorkspaceOptions(preferredWorkspaceId?: string) {
  workspaceLoading.value = true
  return WorkspaceApi.getSystemWorkspaceList()
    .then((workspaces) => {
      workspacesList.value = workspaces
      currentWorkspace.value = workspaces.find(({ id }) => id === preferredWorkspaceId) ?? workspaces[0]
      paginationConfig.value.currentPage = 1
      return loadWorkspaceMembers()
    })
    .finally(() => {
      workspaceLoading.value = false
    })
}

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  currentWorkspace.value = workspace
  paginationConfig.value.currentPage = 1
  return loadWorkspaceMembers()
}

/* 删除工作空间 */
function handleWorkspaceDelete(workspace: WorkspaceItem) {
  if (!workspace.id || workspace.id === 'default') return

  WorkspaceApi.getWorkspaceDeleteCheck(workspace.id)
    .then(() =>
      MsgConfirm(`${t('workspace.delete.title')}: ${workspace.name}?`, t('workspace.delete.description')).then(() => {
        workspaceLoading.value = true
        return WorkspaceApi.deleteWorkspace(workspace.id as string)
          .then(() => {
            MsgSuccess(t('common.messages.deleteSuccess'))
            // 删除未选中的空间也要刷新列表，并保留当前选中项。
            return loadWorkspaceOptions(currentWorkspace.value?.id)
          })
          .finally(() => {
            workspaceLoading.value = false
          })
      }),
    )

    .catch(() => {})
}

/* 成员列表相关 */
const workspaceMembersLoading = ref(false)
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const memberSearchQuery = ref<Dict<unknown>>()
const memberSearchFields = computed<OptionItem<string>[]>(() => [
  { label: t('user.name.label'), value: 'nick_name' },
  { label: t('user.username.label'), value: 'username' },
])
const workspaceMembers = ref<WorkspaceMemberItem[]>([])
const workspaceMemberTableRef = useTemplateRef<{ clearSelection: () => void }>('workspaceMemberTableRef')
function handleMemberSearch(query?: Dict<unknown>) {
  memberSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  return loadWorkspaceMembers()
}

function clearMemberSelection() {
  workspaceMemberTableRef.value?.clearSelection()
  batchSelectedMembers.value = []
}

function loadWorkspaceMembers() {
  clearMemberSelection()
  const workspaceId = currentWorkspace.value?.id
  if (!workspaceId) {
    workspaceMembers.value = []
    paginationConfig.value.total = 0
    return Promise.resolve()
  }
  workspaceMembersLoading.value = true
  return WorkspaceApi.getWorkspaceMemberList(workspaceId, paginationConfig.value, memberSearchQuery.value)
    .then((res) => {
      workspaceMembers.value = res.records
      paginationConfig.value.total = res.total
    })
    .finally(() => {
      workspaceMembersLoading.value = false
    })
}

/** 同一用户的选择框、姓名和用户名按连续记录合并。 */
function objectSpanMethod({
  column,
  row,
  rowIndex,
}: {
  row: WorkspaceMemberItem
  column: TableColumnCtx<WorkspaceMemberItem>
  rowIndex: number
  columnIndex: number
}) {
  const shouldMerge = column.type === 'selection' || column.property === 'nick_name' || column.property === 'username'
  if (!shouldMerge) return

  const userId = row.user_id
  if (workspaceMembers.value[rowIndex - 1]?.user_id === userId) return [0, 0]

  let rowspan = 1
  while (workspaceMembers.value[rowIndex + rowspan]?.user_id === userId) rowspan += 1
  return [rowspan, 1]
}

function getWorkspaceMemberRowKey(member: WorkspaceMemberItem) {
  return `${member.user_relation_id}:${member.role_id}`
}

/* 添加成员drawer */
const addMemberDrawerRef = useTemplateRef<InstanceType<typeof AddMemberDrawer>>('addMemberDrawerRef')

function handleOpenAddMemberDrawer() {
  addMemberDrawerRef.value?.open()
}

/* 删除成员 */
function handleRemoveMember(member: WorkspaceMemberItem) {
  const workspaceId = currentWorkspace.value?.id
  if (!workspaceId) return

  MsgConfirm(`${t('system.member.removeTitle')}: ${member.nick_name}?`, '', { confirmButtonText: t('common.actions.remove') })
    .then(() => {
      workspaceMembersLoading.value = true
      return WorkspaceApi.postRemoveWorkspaceMember(workspaceId, member.user_relation_id).then(() => {
        MsgSuccess(t('common.messages.removeSuccess'))
        return loadWorkspaceMembers()
      })
    })
    .catch(() => {})
    .finally(() => {
      workspaceMembersLoading.value = false
    })
}

/* 批量删除成员 */
const batchSelectedMembers = ref<WorkspaceMemberItem[]>([])

function handleBatchDelete() {
  const workspaceId = currentWorkspace.value?.id
  if (!workspaceId || workspaceLoading.value || workspaceMembersLoading.value || !batchSelectedMembers.value.length) return

  const selectedMembers = [...batchSelectedMembers.value]
  const memberCount = new Set(selectedMembers.map(({ user_id }) => user_id)).size
  const userRelationIds = [...new Set(selectedMembers.map(({ user_relation_id }) => user_relation_id))]
  MsgConfirm(
    `${t('workspace.delete.batchRemoveTitle')}?`,
    t('workspace.delete.batchRemoveDescription', { memberCount, recordCount: selectedMembers.length }),
    { confirmButtonText: t('common.actions.remove') },
  )
    .then(() => {
      workspaceMembersLoading.value = true
      return WorkspaceApi.postBatchRemoveWorkspaceMembers(workspaceId, userRelationIds).then(({ success_count, failed_count }) => {
        if (failed_count > 0) {
          MsgSuccess(t('workspace.delete.partialRemoveMessage', { successCount: success_count, failedCount: failed_count }, success_count))
        } else {
          MsgSuccess(t('common.messages.removeSuccess'))
        }
        return loadWorkspaceMembers()
      })
    })
    .catch(() => {})
    .finally(() => {
      workspaceMembersLoading.value = false
    })
}

function handleBatchSelectionChange(selection: unknown[]) {
  batchSelectedMembers.value = selection as WorkspaceMemberItem[]
}

onMounted(() => loadWorkspaceOptions())
</script>

<template>
  <MkViewLayout :title="t('workspace.title')" class="system-identity-workspaces" :loading="workspaceLoading">
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <!-- 创建工作空间 -->
        <MkTooltip :content="t('workspace.createTitle')" placement="top" v-if="perm.system.workspace.create()">
          <el-button text type="primary" class="-mr-1" @click="handleOpenWorkspaceDialog()">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>
      <MkSearchList :data="workspacesList" :default-active="currentWorkspace?.id" @click="handleWorkspaceSelect">
        <template #action-dropdown="{ row: workspace }">
          <!-- 重命名工作空间 -->
          <MkDropdownItem v-if="perm.system.workspace.edit()" @click="handleOpenWorkspaceDialog(workspace)">
            <template #icon>
              <MkIcon name="icon_rename_outlined" />
            </template>
            <span>{{ t('common.actions.rename') }}</span>
          </MkDropdownItem>
          <!-- 删除工作空间 -->
          <MkDropdownItem v-if="perm.system.workspace.delete()" :disabled="workspace.id === 'default'" @click="handleWorkspaceDelete(workspace)">
            <template #icon>
              <MkIcon name="icon_delete-trash_outlined" />
            </template>
            <span>{{ t('common.actions.delete') }}</span>
          </MkDropdownItem>
        </template>
      </MkSearchList>
    </template>

    <template #default="{ Header }">
      <template v-if="currentWorkspace">
        <component :is="Header">
          <div class="flex-align-center min-w-0 flex-1 gap-2">
            <h4 class="min-w-0 truncate" :title="currentWorkspace.name">
              {{ currentWorkspace.name }}
            </h4>
            <el-divider direction="vertical" />
            <span class="flex-align-center text-N500">
              <MkIcon name="icon_member_filled" class="mr-1" />
              {{ currentWorkspace.user_count }}
            </span>
          </div>
        </component>

        <div class="flex-between mb-4">
          <div>
            <!-- 添加成员 -->
            <el-button v-if="perm.system.workspace.addMember()" type="primary" @click="handleOpenAddMemberDrawer">
              <MkIcon name="icon_add_outlined" />
              <span>{{ t('system.member.add') }}</span>
            </el-button>
          </div>

          <MkComplexSearch :fields="memberSearchFields" @change="handleMemberSearch" />
        </div>

        <MkTable
          ref="workspaceMemberTableRef"
          v-model:pagination-config="paginationConfig"
          :data="workspaceMembers"
          selection-group-key="user_id"
          v-loading="workspaceMembersLoading"
          @current-change="loadWorkspaceMembers()"
          @size-change="loadWorkspaceMembers()"
          @selection-change="handleBatchSelectionChange"
          :span-method="objectSpanMethod"
          :max-table-height="280"
          :row-key="getWorkspaceMemberRowKey"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column prop="nick_name" :label="t('user.name.label')" />
          <el-table-column prop="username" :label="t('user.username.label')" />
          <el-table-column prop="role_name" :label="t('user.role.label')" class-name="border-l!" />
          <el-table-column :label="t('common.labels.operation')" width="80" fixed="right">
            <template #default="{ row }">
              <!-- 移除成员 -->
              <MkTooltip :content="t('common.actions.remove')" placement="top" v-if="perm.system.workspace.removeMember()">
                <el-button type="primary" text @click="handleRemoveMember(row)">
                  <MkIcon name="icon_assigned_outlined" />
                </el-button>
              </MkTooltip>
            </template>
          </el-table-column>

          <template #footer-batch-actions>
            <!-- 批量移除成员 -->
            <el-button v-if="perm.system.workspace.removeMember()" type="danger" plain @click="handleBatchDelete">
              {{ t('common.actions.remove') }}
            </el-button>
          </template>
        </MkTable>
      </template>
      <MkEmpty v-else class="flex-1" />
    </template>
  </MkViewLayout>
  <CreateOrUpdateWorkspaceDialog ref="workspaceDialogRef" @refresh="loadWorkspaceOptions" />
  <AddMemberDrawer ref="addMemberDrawerRef" :current-workspace="currentWorkspace" @refresh="loadWorkspaceOptions" />
</template>
