<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import type { TableColumnCtx } from 'element-plus'
import type { RequestParams, OptionItem, WorkspaceItem, WorkspaceMemberItem } from '@/api/types'
import WorkspaceApi from '@/api/admin/system/workspace'
import MkSearchList from '@/components/mk-search-list/index.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import AddMemberDrawer from './AddMemberDrawer.vue'
import CreateOrUpdateWorkspaceDialog from './dialog/CreateOrUpdateWorkspaceDialog.vue'

const route = useRoute()

/* 添加工作空间表单dialog */
const workspaceDialogRef =
  useTemplateRef<InstanceType<typeof CreateOrUpdateWorkspaceDialog>>('workspaceDialogRef')

/* 选择工作空间列表 */
const workspaceLoading = ref(false)
const currentWorkspace = ref<WorkspaceItem>()
const workspacesList = ref<WorkspaceItem[]>([])

function loadWorkspaceOptions(preferredWorkspaceId?: string) {
  workspaceLoading.value = true
  return WorkspaceApi.getSystemWorkspaceList()
    .then((workspaces) => {
      workspacesList.value = workspaces
      currentWorkspace.value =
        workspaces.find(({ id }) => id === preferredWorkspaceId) ?? workspaces[0]
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
  if (!workspace.id) return

  WorkspaceApi.getWorkspaceDeleteCheck(workspace.id)
    .then(() =>
      MsgConfirm(
        `确认删除${workspace.name}？`,
        '删除后，该空间下的成员都会被移除，请谨慎操作。',
      ).then(() => {
        workspaceLoading.value = true
        return WorkspaceApi.deleteWorkspace(workspace.id as string).then(() => {
          MsgSuccess('删除成功')
          if (currentWorkspace.value?.id === workspace.id) {
            return loadWorkspaceOptions()
          }
        })
      }),
    )

    .catch(() => {})
}

/* 成员列表相关 */
const workspaceMembersLoading = ref(false)
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})
const memberSearchQuery = ref<RequestParams>()
const memberSearchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'name' },
]
const workspaceMembers = ref<WorkspaceMemberItem[]>([])
function handleMemberSearch(query?: RequestParams) {
  memberSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  return loadWorkspaceMembers()
}

function loadWorkspaceMembers() {
  const workspaceId = currentWorkspace.value?.id
  if (!workspaceId) {
    workspaceMembers.value = []
    paginationConfig.value.total = 0
    return Promise.resolve()
  }
  workspaceMembersLoading.value = true
  return WorkspaceApi.getWorkspaceMemberList(
    workspaceId,
    paginationConfig.value,
    memberSearchQuery.value,
  )
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
  const shouldMerge =
    column.type === 'selection' || column.property === 'nick_name' || column.property === 'username'
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
const addMemberDrawerRef =
  useTemplateRef<InstanceType<typeof AddMemberDrawer>>('addMemberDrawerRef')

/* 删除成员 */
function handleRemoveMember(member: WorkspaceMemberItem) {
  const workspaceId = currentWorkspace.value?.id
  if (!workspaceId) return

  MsgConfirm(`是否移除成员：${member.nick_name}？`)
    .then(() => {
      workspaceMembersLoading.value = true
      return WorkspaceApi.postRemoveWorkspaceMember(workspaceId, member.user_relation_id).then(
        () => {
          MsgSuccess('移除成功')
          return loadWorkspaceMembers()
        },
      )
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
  if (!workspaceId) return

  MsgConfirm(`是否删除选中的 ${batchSelectedMembers.value.length} 个成员？`, '')
    .then(() => {
      workspaceMembersLoading.value = true
      return WorkspaceApi.postBatchRemoveWorkspaceMembers(
        workspaceId,
        batchSelectedMembers.value.map(({ user_relation_id }) => user_relation_id),
      ).then(({ success_count, failed_count }) => {
        if (failed_count > 0) {
          MsgSuccess(`移除成功 ${success_count} 个成员，失败 ${failed_count} 个`)
        } else {
          MsgSuccess('移除成功')
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
  <div class="system-identity-workspaces flex h-full" v-loading="workspaceLoading">
    <aside class="flex w-sidebar-expanded shrink-0 flex-col border-r">
      <header class="flex-between p-4">
        <h4>{{ route.meta.title }}</h4>
        <el-tooltip content="创建工作空间" placement="top">
          <el-button text type="primary" class="-mr-1" @click="workspaceDialogRef?.open()">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </el-tooltip>
      </header>
      <MkSearchList
        :data="workspacesList"
        :default-active="currentWorkspace?.id"
        @click="handleWorkspaceSelect"
      >
        <template #action-dropdown="{ row: workspace }">
          <MkDropdownMenu>
            <MkDropdownItem @click="workspaceDialogRef?.open(workspace)">
              <template #icon>
                <MkIcon name="icon_edit_outlined" />
              </template>
              <span>重命名</span>
            </MkDropdownItem>
            <MkDropdownItem divided @click="handleWorkspaceDelete(workspace)">
              <template #icon>
                <MkIcon name="icon_delete-trash_outlined" />
              </template>
              <span>删除</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkSearchList>
    </aside>

    <section class="min-w-0 flex-1 px-6">
      <header class="py-4 flex items-center gap-2">
        <h4>{{ currentWorkspace?.name }}</h4>
        <el-divider direction="vertical" />
        <span class="flex items-center text-N500">
          <MkIcon name="icon_member_filled" class="mr-1" />
          {{ currentWorkspace?.user_count }}
        </span>
      </header>
      <div class="flex-between mb-4">
        <el-button type="primary" @click="addMemberDrawerRef?.open()">
          <MkIcon name="icon_add_outlined" />
          <span>添加成员</span>
        </el-button>
        <MkComplexSearch :fields="memberSearchFields" @change="handleMemberSearch" />
      </div>

      <MkTable
        v-model:pagination-config="paginationConfig"
        :data="workspaceMembers"
        v-loading="workspaceMembersLoading"
        @current-change="loadWorkspaceMembers()"
        @size-change="loadWorkspaceMembers()"
        @selection-change="handleBatchSelectionChange"
        :span-method="objectSpanMethod"
        :row-key="getWorkspaceMemberRowKey"
      >
        <el-table-column type="selection" width="64" />
        <el-table-column prop="nick_name" label="姓名" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role_name" label="角色" class-name="border-l!" />
        <el-table-column label="操作" width="70" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="移除" placement="top">
              <el-button type="primary" text @click="handleRemoveMember(row)">
                <MkIcon name="icon_assigned_outlined" />
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>

        <template #footer-batch-actions>
          <el-button type="danger" plain @click="handleBatchDelete">移除</el-button>
        </template>
      </MkTable>
    </section>

    <CreateOrUpdateWorkspaceDialog ref="workspaceDialogRef" @refresh="loadWorkspaceOptions" />
    <AddMemberDrawer
      ref="addMemberDrawerRef"
      :current-workspace="currentWorkspace"
      @refresh="loadWorkspaceOptions"
    />
  </div>
</template>
