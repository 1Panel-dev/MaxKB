<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import type ResourceAuthorizationApi from '@/api/admin/workspace/resource-authorization'
import type SystemResourceAuthorizationApi from '@/api/admin/system/resource-management/resource-authorization'
import { RESOURCE_PERMISSION } from '@/api/enums'
import type { Dict, ResourcePermission, ResourceUserPermission } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import MkTable from '@/components/global/mk-table/index.vue'
import PermissionConfigDialog from './PermissionConfigDialog.vue'
import { useStore } from '@/stores'

import type { ResourceAuthorizationContentProps, ResourcePermissionOption } from './types'

interface Props extends ResourceAuthorizationContentProps {
  api: typeof ResourceAuthorizationApi | typeof SystemResourceAuthorizationApi
  permissionOptions: ResourcePermissionOption[]
}

const props = defineProps<Props>()
const emit = defineEmits<{ refresh: [] }>()
const submitting = defineModel<boolean>('submitting', { required: true })

/* 查询与跨页选择 */
const { auth } = useStore()
const searchFields = computed(() => [
  { label: '姓名', value: 'nick_name' },
  { label: '用户名', value: 'username' },
  { label: '权限', value: 'permission', multiple: true, options: props.permissionOptions },
  ...(auth.isEE || auth.isPE ? [{ label: '角色', value: 'role' }] : []),
])
const loading = ref(false)
const permissionUsers = ref<ResourceUserPermission[]>([])
const selectedUsers = ref<ResourceUserPermission[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const tableRef = useTemplateRef('tableRef')

function loadPermissions() {
  if (!props.targetId) return Promise.resolve()
  loading.value = true
  return props.api
    .getResourceAuthorization(props.targetId, props.type, paginationConfig.value, searchQuery.value)
    .then(({ records, total }) => {
      permissionUsers.value = records.map((subject) => ({
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
  selectedUsers.value = []
  tableRef.value?.clearSelection()
}

function handleSearch(query?: Dict<unknown>) {
  searchQuery.value = query
  paginationConfig.value.currentPage = 1
  clearSelection()
  loadPermissions()
}

function handleSelectionChange(selection: unknown[]) {
  selectedUsers.value = selection as ResourceUserPermission[]
}

/* 单项与批量保存：确认前不修改行数据，失败时保留待提交配置。 */
const configDialogRef = useTemplateRef<InstanceType<typeof PermissionConfigDialog>>('configDialogRef')
const pendingUserIds = ref<string[]>([])

function handleOpenBatchConfig() {
  if (!selectedUsers.value.length || submitting.value) return
  pendingUserIds.value = selectedUsers.value.map(({ id }) => id)
  configDialogRef.value?.open()
}

function handlePermissionChange(value: string | number | boolean | undefined, subject: ResourceUserPermission) {
  const permission = props.editablePermissionOptions.find((option) => option.value === value)?.value
  if (!permission || permission === subject.permission || submitting.value) return
  pendingUserIds.value = [subject.id]
  if (props.isFolder) {
    configDialogRef.value?.open(permission)
  } else {
    submitPermissions(permission, false)
  }
}

function submitPermissions(permission: ResourcePermission, includeChildren: boolean) {
  if (submitting.value || !pendingUserIds.value.length || (includeChildren && !props.managedFolderIds.length)) return
  const permissionScope = {
    permission,
    include_children: includeChildren,
    ...(includeChildren ? { folder_ids: [...props.managedFolderIds] } : {}),
  }
  submitting.value = true
  return props.api
    .putResourceAuthorization(
      props.targetId,
      props.type,
      pendingUserIds.value.map((id) => ({ user_id: id, ...permissionScope })),
    )
    .then(() => {
      MsgSuccess('提交成功')
      configDialogRef.value?.close()
      pendingUserIds.value = []
      clearSelection()
      emit('refresh')
      return loadPermissions()
    })
    .finally(() => {
      submitting.value = false
    })
}

/* 挂载当前标签时查询权限。 */
onMounted(() => loadPermissions())
</script>

<template>
  <div>
    <div class="flex-between mb-4 gap-4">
      <el-button type="primary" :disabled="!selectedUsers.length || loading || submitting" @click="handleOpenBatchConfig">配置权限</el-button>
      <MkComplexSearch :fields="searchFields" @change="handleSearch" />
    </div>
    <MkTable
      ref="tableRef"
      v-loading="loading || submitting"
      v-model:pagination-config="paginationConfig"
      :data="permissionUsers"
      :max-table-height="260"
      @current-change="loadPermissions"
      @size-change="loadPermissions"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="40" reserve-selection />
      <el-table-column prop="nick_name" label="姓名" min-width="120" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" min-width="120" show-overflow-tooltip />
      <el-table-column v-if="auth.isEE || auth.isPE" label="角色" width="160">
        <template #default="{ row }">
          <MkTagGroup v-if="row.role_name?.length" :tags="row.role_name" />
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="权限" min-width="340">
        <template #default="{ row }">
          <el-radio-group :model-value="row.permission" :disabled="submitting" @change="handlePermissionChange($event, row)">
            <el-radio v-for="option in editablePermissionOptions" :key="option.value" :value="option.value" class="mr-4!">{{
              option.label
            }}</el-radio>
          </el-radio-group>
        </template>
      </el-table-column>
    </MkTable>
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
