<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import ResourceAuthorizationApi from '@/api/admin/workspace/resource-authorization'
import SystemResourceAuthorizationApi from '@/api/admin/system/resource-management/resource-authorization'
import { RESOURCE_AUTHORIZATION_TARGET_TYPE as TARGET, RESOURCE_PERMISSION } from '@/api/enums'
import type { FolderItem, ResourceAuthorizationTargetType } from '@/api/types'
import { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'
import { buildBaseResourcePermission, hasPermission, PermissionConstants as P, Role, RoleConstants } from '@/permission/core'
import { useStore } from '@/stores'
import { getWorkspaceId, isSystemResource } from '@/utils/resource-context'
import UserAuthorization from './UserAuthorization.vue'
import UserGroupAuthorization from './user-group/UserGroupAuthorization.vue'

defineOptions({ name: 'ResourceAuthorizationDrawer' })
const props = defineProps<{
  type: ResourceAuthorizationTargetType
  isFolder?: boolean
  isRootFolder?: boolean
}>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
const { auth } = useStore()

/* 抽屉和当前授权对象 */
const drawerVisible = ref(false)
const targetType = ref<'user-group' | 'user'>('user-group')
const targetId = ref('')
const folderData = ref<FolderItem>()
const submitting = ref(false)

/* System 资源管理使用专属用户授权接口，用户组沿用现有接口。 */
const userAuthorizationApi = computed(() => (isSystemResource() ? SystemResourceAuthorizationApi : ResourceAuthorizationApi))

/* 资源类型与权限选项 */
const folderPermissionMap = {
  [TARGET.APPLICATION]: { target: TARGET.APPLICATION_FOLDER, edit: P.APPLICATION_FOLDER_EDIT, auth: P.APPLICATION_RESOURCE_AUTHORIZATION },
  [TARGET.KNOWLEDGE]: { target: TARGET.KNOWLEDGE_FOLDER, edit: P.KNOWLEDGE_FOLDER_EDIT, auth: P.KNOWLEDGE_RESOURCE_AUTHORIZATION },
  [TARGET.TOOL]: { target: TARGET.TOOL_FOLDER, edit: P.TOOL_FOLDER_EDIT, auth: P.TOOL_RESOURCE_AUTHORIZATION },
}
const folderPermissions = computed(() => {
  switch (props.type) {
    case TARGET.APPLICATION:
    case TARGET.APPLICATION_FOLDER:
      return folderPermissionMap[TARGET.APPLICATION]
    case TARGET.KNOWLEDGE:
    case TARGET.KNOWLEDGE_FOLDER:
      return folderPermissionMap[TARGET.KNOWLEDGE]
    case TARGET.TOOL:
    case TARGET.TOOL_FOLDER:
      return folderPermissionMap[TARGET.TOOL]
    default:
      return undefined
  }
})
const isFolder = computed(() => Boolean(folderPermissions.value && (props.isFolder || props.isRootFolder || props.type.endsWith('_FOLDER'))))
const authorizationType = computed(() => (isFolder.value ? (folderPermissions.value?.target ?? props.type) : props.type))
const permissionOptions = computed(() => RESOURCE_PERMISSION_OPTIONS.filter(({ value }) => !auth.isCE || value !== RESOURCE_PERMISSION.ROLE))
const editablePermissionOptions = computed(() =>
  permissionOptions.value.filter(({ value }) => !props.isRootFolder || value !== RESOURCE_PERMISSION.NOT_AUTH),
)
/* 子资源范围：直接使用路由中的工作空间鉴权。 */
const managedFolderIds = computed(() => {
  const permissions = folderPermissions.value
  if (!folderData.value || !permissions) return []
  const canManageAll = hasPermission(
    [RoleConstants.ADMIN, new Role(RoleConstants.WORKSPACE_MANAGE.name, getWorkspaceId()), permissions.auth.getWorkspaceManageFlagPermission()],
    undefined,
    { workspaceId: getWorkspaceId() },
  )
  const folderEditPermission = permissions.edit
  function collectFolders(folder: FolderItem): string[] {
    const canManage = canManageAll || hasPermission(buildBaseResourcePermission(folderEditPermission, folder.id, getWorkspaceId()))
    return [...(canManage ? [folder.id] : []), ...(folder.children ?? []).flatMap(collectFolders)]
  }
  return collectFolders(folderData.value)
})

/* 抽屉生命周期 */
function open(id: string, folder?: FolderItem) {
  targetId.value = id
  folderData.value = folder ? cloneDeep(folder) : undefined
  drawerVisible.value = true
}

function resetData() {
  targetType.value = 'user-group'
  targetId.value = ''
  folderData.value = undefined
  submitting.value = false
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="drawerVisible" title="资源授权" :size="920" :show-close="!submitting" @closed="handleClosed">
    <el-tabs v-model="targetType" :before-leave="() => !submitting">
      <el-tab-pane label="按用户组" name="user-group" />
      <el-tab-pane label="按用户" name="user" />
    </el-tabs>
    <div class="mt-4">
      <UserGroupAuthorization
        v-if="targetType === 'user-group' && targetId"
        :key="targetId"
        v-model:submitting="submitting"
        :api="ResourceAuthorizationApi"
        :target-id="targetId"
        :type="authorizationType"
        :is-folder="isFolder"
        :is-root-folder="isRootFolder"
        :managed-folder-ids="managedFolderIds"
        :editable-permission-options="editablePermissionOptions"
        @refresh="emit('refresh')"
      />

      <UserAuthorization
        v-if="targetType === 'user' && targetId"
        :key="targetId"
        v-model:submitting="submitting"
        :api="userAuthorizationApi"
        :target-id="targetId"
        :type="authorizationType"
        :is-folder="isFolder"
        :is-root-folder="isRootFolder"
        :managed-folder-ids="managedFolderIds"
        :permission-options="permissionOptions"
        :editable-permission-options="editablePermissionOptions"
        @refresh="emit('refresh')"
      />
    </div>
  </MkDrawer>
</template>
