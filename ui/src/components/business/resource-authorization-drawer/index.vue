<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type ResourceAuthorizationApi from '@/api/admin/workspace/resource-authorization'
import { RESOURCE_AUTHORIZATION_TARGET_TYPE as TARGET, RESOURCE_PERMISSION } from '@/api/enums'
import type {
  Dict,
  FolderItem,
  ResourceAuthorizationTargetType,
  ResourcePermission,
  ResourceUserPermission,
  ResourceUserPermissionPayload,
} from '@/api/types'
import { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'
import { buildBaseResourcePermission, hasPermission, PermissionConstants as P, Role, RoleConstants } from '@/permission/core'
import { useStore } from '@/stores'
import { getWorkspaceId } from '@/utils/resource-context'
import { MsgSuccess } from '@/utils/message'
import MkTable from '@/components/global/mk-table/index.vue'
import PermissionConfigDialog from './PermissionConfigDialog.vue'

defineOptions({ name: 'ResourceAuthorizationDrawer' })
const props = defineProps<{
  api: typeof ResourceAuthorizationApi
  type: ResourceAuthorizationTargetType
  isFolder?: boolean
  isRootFolder?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()

/* 资源类型与权限选项 */
const folderPermissionMap = {
  [TARGET.APPLICATION]: { target: TARGET.APPLICATION_FOLDER, edit: P.APPLICATION_FOLDER_EDIT, auth: P.APPLICATION_RESOURCE_AUTHORIZATION },
  [TARGET.KNOWLEDGE]: { target: TARGET.KNOWLEDGE_FOLDER, edit: P.KNOWLEDGE_FOLDER_EDIT, auth: P.KNOWLEDGE_RESOURCE_AUTHORIZATION },
  [TARGET.TOOL]: { target: TARGET.TOOL_FOLDER, edit: P.TOOL_FOLDER_EDIT, auth: P.TOOL_RESOURCE_AUTHORIZATION },
}
const resourceType = computed(() => props.type.replace('_FOLDER', '') as keyof typeof folderPermissionMap | typeof TARGET.MODEL)
const folderPermissions = computed(() => (resourceType.value === TARGET.MODEL ? undefined : folderPermissionMap[resourceType.value]))
const isFolder = computed(() => Boolean(folderPermissions.value && (props.isFolder || props.isRootFolder || props.type.endsWith('_FOLDER'))))
const authorizationType = computed(() => (isFolder.value ? folderPermissions.value!.target : props.type))
const permissionOptions = computed(() => RESOURCE_PERMISSION_OPTIONS.filter(({ value }) => !auth.isCE || value !== RESOURCE_PERMISSION.ROLE))
const editablePermissionOptions = computed(() =>
  permissionOptions.value.filter(({ value }) => !props.isRootFolder || value !== RESOURCE_PERMISSION.NOT_AUTH),
)
const searchFields = computed(() => [
  { label: '姓名', value: 'nick_name' },
  { label: '用户名', value: 'username' },
  { label: '权限', value: 'permission', multiple: true, options: permissionOptions.value },
  ...(auth.isEE || auth.isPE ? [{ label: '角色', value: 'role' }] : []),
])

/* 查询与跨页选择 */
const drawerVisible = ref(false)
const workspaceId = ref('')
const targetId = ref('')
const folderData = ref<FolderItem>()
const loading = ref(false)
const submitting = ref(false)
const permissionUsers = ref<ResourceUserPermission[]>([])
const selectedUsers = ref<ResourceUserPermission[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const tableRef = useTemplateRef('tableRef')
let requestId = 0
let sessionId = 0

function loadPermissions() {
  if (!targetId.value) return Promise.resolve()
  const currentRequestId = ++requestId
  loading.value = true
  return props.api
    .getResourceAuthorization(workspaceId.value, targetId.value, authorizationType.value, paginationConfig.value, searchQuery.value)
    .then(({ records, total }) => {
      if (currentRequestId !== requestId) return
      permissionUsers.value = records.map((user) => ({
        ...user,
        permission: props.isRootFolder && user.permission === RESOURCE_PERMISSION.NOT_AUTH ? RESOURCE_PERMISSION.VIEW : user.permission,
      }))
      paginationConfig.value.total = total
    })
    .finally(() => {
      if (currentRequestId === requestId) loading.value = false
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

/* 子资源范围：使用目标工作空间鉴权，不依赖路由路径推断。 */
const managedFolderIds = computed(() => {
  const permissions = folderPermissions.value
  if (!folderData.value || !permissions) return []
  const canManageAll = hasPermission(
    [RoleConstants.ADMIN, new Role(RoleConstants.WORKSPACE_MANAGE.name, workspaceId.value), permissions.auth.getWorkspaceManageFlagPermission()],
    undefined,
    { workspaceId: workspaceId.value },
  )
  function collectFolders(folder: FolderItem): string[] {
    const canManage = canManageAll || hasPermission(buildBaseResourcePermission(permissions!.edit, folder.id, workspaceId.value))
    return [...(canManage ? [folder.id] : []), ...(folder.children ?? []).flatMap(collectFolders)]
  }
  return collectFolders(folderData.value)
})

/* 单项与批量保存：确认前不修改行数据，失败时保留待提交配置。 */
const configDialogRef = useTemplateRef<InstanceType<typeof PermissionConfigDialog>>('configDialogRef')
const pendingUserIds = ref<string[]>([])

function handleOpenBatchConfig() {
  if (!selectedUsers.value.length || submitting.value) return
  pendingUserIds.value = selectedUsers.value.map(({ id }) => id)
  configDialogRef.value?.open()
}

function handlePermissionChange(value: string | number | boolean | undefined, user: ResourceUserPermission) {
  const permission = editablePermissionOptions.value.find((option) => option.value === value)?.value
  if (!permission || permission === user.permission || submitting.value) return
  pendingUserIds.value = [user.id]
  if (isFolder.value) {
    configDialogRef.value?.open(permission)
  } else {
    submitPermissions(permission, false)
  }
}

function submitPermissions(permission: ResourcePermission, includeChildren: boolean) {
  if (submitting.value || !pendingUserIds.value.length || (includeChildren && !managedFolderIds.value.length)) return
  const currentSessionId = sessionId
  const permissions: ResourceUserPermissionPayload[] = pendingUserIds.value.map((userId) => ({
    user_id: userId,
    permission,
    include_children: includeChildren,
    ...(includeChildren ? { folder_ids: [...managedFolderIds.value] } : {}),
  }))
  submitting.value = true
  return props.api
    .putResourceAuthorization(workspaceId.value, targetId.value, authorizationType.value, permissions)
    .then(() => {
      if (currentSessionId !== sessionId) return
      MsgSuccess('提交成功')
      configDialogRef.value?.close()
      pendingUserIds.value = []
      clearSelection()
      emit('refresh')
      return loadPermissions()
    })
    .finally(() => {
      if (currentSessionId === sessionId) submitting.value = false
    })
}

/* 抽屉生命周期 */
function resetData() {
  sessionId += 1
  requestId += 1
  targetId.value = ''
  workspaceId.value = ''
  folderData.value = undefined
  permissionUsers.value = []
  searchQuery.value = undefined
  paginationConfig.value = { currentPage: 1, pageSize: 20, total: 0 }
  pendingUserIds.value = []
  loading.value = false
  submitting.value = false
  clearSelection()
}

function open(id: string, folder?: FolderItem, resourceWorkspaceId?: string) {
  resetData()
  targetId.value = id
  workspaceId.value = resourceWorkspaceId ?? folder?.workspace_id ?? getWorkspaceId() ?? 'default'
  folderData.value = folder ? cloneDeep(folder) : undefined
  drawerVisible.value = true
  loadPermissions()
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="drawerVisible" title="资源授权" size="850" :show-close="!submitting" @closed="resetData">
    <div class="flex-between mb-4 gap-4">
      <el-button type="primary" :disabled="!selectedUsers.length || loading || submitting" @click="handleOpenBatchConfig">配置权限</el-button>
      <MkComplexSearch :fields="searchFields" @change="handleSearch" />
    </div>
    <MkTable
      ref="tableRef"
      v-loading="loading || submitting"
      v-model:pagination-config="paginationConfig"
      :data="permissionUsers"
      :max-table-height="200"
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
  </MkDrawer>
</template>
