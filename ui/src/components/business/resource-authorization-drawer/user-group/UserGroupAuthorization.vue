<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import type ResourceAuthorizationApi from '@/api/admin/workspace/resource-authorization'
import { RESOURCE_PERMISSION } from '@/api/enums'
import type { Dict, ResourcePermission, ResourceUserGroupPermission } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import MkTable from '@/components/global/mk-table/index.vue'
import PermissionConfigDialog from '../PermissionConfigDialog.vue'
import { getWorkspaceId } from '@/utils/resource-context'
import UserGroupMembersDrawer from './UserGroupMembersDrawer.vue'

import type { ResourceAuthorizationContentProps } from '../types'

interface Props extends ResourceAuthorizationContentProps {
  api: typeof ResourceAuthorizationApi
}

const props = defineProps<Props>()
const emit = defineEmits<{ refresh: [] }>()
const submitting = defineModel<boolean>('submitting', { required: true })

/* 查询与跨页选择 */
const searchFields = [{ label: '名称', value: 'name' }]
const loading = ref(false)
const permissionGroups = ref<ResourceUserGroupPermission[]>([])
const selectedGroups = ref<ResourceUserGroupPermission[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 10, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const tableRef = useTemplateRef('tableRef')

function loadPermissions() {
  if (!props.targetId) return Promise.resolve()
  loading.value = true
  return props.api
    .getResourceUserGroupAuthorization(props.targetId, props.type, paginationConfig.value, searchQuery.value)
    .then(({ records, total }) => {
      permissionGroups.value = records.map((subject) => ({
        ...subject,
        permission: props.isRootFolder && subject.permission === RESOURCE_PERMISSION.NOT_AUTH ? RESOURCE_PERMISSION.VIEW : subject.permission,
      }))
      paginationConfig.value.total = total
    })
    .finally(() => {
      loading.value = false
    })
}

function clearSelection() {
  selectedGroups.value = []
  tableRef.value?.clearSelection()
}

function handleSearch(query?: Dict<unknown>) {
  searchQuery.value = query
  paginationConfig.value.currentPage = 1
  clearSelection()
  loadPermissions()
}

/* 查看用户组成员 */
const membersDrawerRef = useTemplateRef<InstanceType<typeof UserGroupMembersDrawer>>('membersDrawerRef')

function handleOpenMembersDrawer(group: ResourceUserGroupPermission) {
  const workspaceId = getWorkspaceId()
  if (!workspaceId) return
  membersDrawerRef.value?.open({ ...group, workspace_id: workspaceId })
}

function handleSelectionChange(selection: unknown[]) {
  selectedGroups.value = selection as ResourceUserGroupPermission[]
}

/* 单项与批量保存：确认前不修改行数据，失败时保留待提交配置。 */
const configDialogRef = useTemplateRef<InstanceType<typeof PermissionConfigDialog>>('configDialogRef')
const pendingGroupIds = ref<string[]>([])

function handleOpenBatchConfig() {
  if (!selectedGroups.value.length || submitting.value) return
  pendingGroupIds.value = selectedGroups.value.map(({ id }) => id)
  configDialogRef.value?.open()
}

function handlePermissionChange(value: string | number | boolean | undefined, subject: ResourceUserGroupPermission) {
  const permission = props.editablePermissionOptions.find((option) => option.value === value)?.value
  if (!permission || permission === subject.permission || submitting.value) return
  pendingGroupIds.value = [subject.id]
  if (props.isFolder) {
    configDialogRef.value?.open(permission)
  } else {
    submitPermissions(permission, false)
  }
}

function submitPermissions(permission: ResourcePermission, includeChildren: boolean) {
  if (submitting.value || !pendingGroupIds.value.length || (includeChildren && !props.managedFolderIds.length)) return
  const permissionScope = {
    permission,
    include_children: includeChildren,
    ...(includeChildren ? { folder_ids: [...props.managedFolderIds] } : {}),
  }
  submitting.value = true
  return props.api
    .putResourceUserGroupAuthorization(
      props.targetId,
      props.type,
      pendingGroupIds.value.map((id) => ({ user_group_id: id, ...permissionScope })),
    )
    .then(() => {
      MsgSuccess('提交成功')
      configDialogRef.value?.close()
      pendingGroupIds.value = []
      clearSelection()
      emit('refresh')
      return loadPermissions()
    })
    .finally(() => {
      submitting.value = false
    })
}

/* 仅挂载当前标签，卸载后忽略未完成的查询响应。 */
onMounted(() => loadPermissions())
</script>

<template>
  <div>
    <div class="flex-between mb-4 gap-4">
      <el-button type="primary" :disabled="!selectedGroups.length || loading || submitting" @click="handleOpenBatchConfig">配置权限</el-button>
      <MkComplexSearch :fields="searchFields" @change="handleSearch" />
    </div>
    <MkTable
      ref="tableRef"
      v-loading="loading || submitting"
      v-model:pagination-config="paginationConfig"
      :data="permissionGroups"
      :max-table-height="260"
      @current-change="loadPermissions"
      @size-change="loadPermissions"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="40" reserve-selection />
      <el-table-column prop="name" label="用户组" min-width="160" show-overflow-tooltip />
      <el-table-column label="成员数" min-width="100">
        <template #default="{ row }">
          <el-link type="primary" @click="handleOpenMembersDrawer(row)">{{ row.count }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="操作权限" min-width="340">
        <template #default="{ row }">
          <el-radio-group :model-value="row.permission" :disabled="submitting" @change="handlePermissionChange($event, row)">
            <el-radio v-for="option in editablePermissionOptions" :key="option.value" :value="option.value" class="mr-4!">{{
              option.label
            }}</el-radio>
          </el-radio-group>
        </template>
      </el-table-column>
    </MkTable>
    <UserGroupMembersDrawer ref="membersDrawerRef" />
    <PermissionConfigDialog
      ref="configDialogRef"
      :options="editablePermissionOptions"
      :is-folder="isFolder"
      :can-include-children="managedFolderIds.length > 0"
      :loading="submitting"
      @submit="submitPermissions"
    />
  </div>
</template>
