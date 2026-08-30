<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import WorkspaceApi from '@/api/admin/system/workspace'
import CommonSystemApi from '@/api/admin/system/common'
import UserGroupsApi from '@/api/admin/system/user-groups'
import ResourceAuthorizationApi from '@/api/admin/system/resource-authorization'
import { RESOURCE_TYPE, RESOURCE_PERMISSION } from '@/api/enums'
import type { ResourceAuthorizationType, ResourcePermissionItem, ResourcePermissionPayload, CommonUserOption, OptionItem, SystemUserGroup, WorkspaceItem } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import PermissionTable from './components/PermissionTable.vue'
import UserAuthorizationList from './components/UserAuthorizationList.vue'
import UserGroupAuthorizationList from './components/UserGroupAuthorizationList.vue'
import { RESOURCE_AUTHORIZATION_LABELS } from './constants'

const { auth } = useStore()
const route = useRoute()

const resourceType = ref<ResourceAuthorizationType>((route.meta.resource as ResourceAuthorizationType) ?? RESOURCE_TYPE.APPLICATION)
const resourceTypeOptions: OptionItem<ResourceAuthorizationType>[] = [RESOURCE_TYPE.APPLICATION, RESOURCE_TYPE.KNOWLEDGE, RESOURCE_TYPE.TOOL, RESOURCE_TYPE.MODEL].map((value) => ({
  label: RESOURCE_AUTHORIZATION_LABELS[value],
  value,
}))

/* 选择工作空间列表 */
const loadingView = ref(false)
const selectedWorkspaceId = ref('default')
const workspaceOptions = ref<WorkspaceItem[]>([])

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
  loadingView.value = true
  loadAuthorizationTargets().finally(() => {
    loadingView.value = false
  })
}

function loadWorkspaceOptions() {
  return WorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
    workspaceOptions.value = workspaces
  })
}

/* 授权对象 */
const targetType = ref<'user-group' | 'user'>('user-group')
const userGroups = ref<SystemUserGroup[]>([])
const workspaceMembers = ref<CommonUserOption[]>([])
const selectedUserGroupId = ref('')
const selectedUserId = ref('')

function loadAuthorizationTargets() {
  return Promise.all([UserGroupsApi.getSystemUserGroups(selectedWorkspaceId.value), CommonSystemApi.getWorkspaceMembers(selectedWorkspaceId.value)]).then(([groups, users]) => {
    userGroups.value = groups
    workspaceMembers.value = users
    selectedUserGroupId.value = groups[0]?.id ?? ''
    selectedUserId.value = users[0]?.id ?? ''
    return loadResourcePermissions()
  })
}

function handleTargetTypeChange() {
  loadResourcePermissions()
}

function handleUserGroupSelect(userGroup: SystemUserGroup) {
  selectedUserGroupId.value = userGroup.id
  loadResourcePermissions()
}

function handleUserSelect(user: CommonUserOption) {
  selectedUserId.value = user.id
  loadResourcePermissions()
}

/* 资源权限 */
const loadingPermissions = ref(false)
const resourcePermissions = ref<ResourcePermissionItem[]>([])

function loadResourcePermissions() {
  const targetId = targetType.value === 'user-group' ? selectedUserGroupId.value : selectedUserId.value

  if (!targetId) {
    resourcePermissions.value = []
    return Promise.resolve()
  }

  loadingPermissions.value = true
  const permissionRequest =
    targetType.value === 'user-group'
      ? ResourceAuthorizationApi.getUserResourcePermissions(selectedWorkspaceId.value, targetId, resourceType.value)
      : ResourceAuthorizationApi.getUserResourcePermissions(selectedWorkspaceId.value, targetId, resourceType.value)

  return permissionRequest
    .then((permissions) => {
      resourcePermissions.value = buildResourceTree(permissions)
    })
    .finally(() => {
      loadingPermissions.value = false
    })
}

function buildResourceTree(resourceItems: ResourcePermissionItem[]) {
  if (resourceType.value === RESOURCE_TYPE.MODEL) return resourceItems

  const resources = resourceItems.map((resource) => ({
    ...resource,
    children: [] as ResourcePermissionItem[],
    permission: !resource.folder_id && resource.permission === RESOURCE_PERMISSION.NOT_AUTH ? RESOURCE_PERMISSION.VIEW : resource.permission,
  }))
  const resourceMap = new Map(resources.map((resource) => [resource.id, resource]))

  resources.forEach((resource) => {
    if (!resource.folder_id) return

    const parentResource = resourceMap.get(resource.folder_id)
    if (parentResource) {
      parentResource.children.push(resource)
    }
  })

  const defaultRoot = resourceMap.get('default')
  if (defaultRoot && !defaultRoot.folder_id) return defaultRoot.children

  return resources.filter(({ folder_id }) => !folder_id)
}

/* 保存权限 */

function handlePermissionsSubmit(permissions: ResourcePermissionPayload[]) {
  const targetId = targetType.value === 'user-group' ? selectedUserGroupId.value : selectedUserId.value

  if (!targetId) return

  loadingPermissions.value = true
  const permissionRequest =
    targetType.value === 'user-group'
      ? ResourceAuthorizationApi.putUserResourcePermissions(selectedWorkspaceId.value, targetId, resourceType.value, permissions)
      : ResourceAuthorizationApi.putUserResourcePermissions(selectedWorkspaceId.value, targetId, resourceType.value, permissions)

  permissionRequest
    .then(() => {
      MsgSuccess('提交成功')
      return loadResourcePermissions()
    })
    .finally(() => {
      loadingPermissions.value = false
    })
}

onMounted(() => {
  loadingView.value = true
  Promise.all(auth.isEE ? [loadWorkspaceOptions(), loadAuthorizationTargets()] : [loadAuthorizationTargets()]).finally(() => {
    loadingView.value = false
  })
})
</script>

<template>
  <MkViewLayout class="system-resource-authorization" :loading="loadingView">
    <template #top v-if="auth.isEE">
      <WorkspaceDropdown v-model="selectedWorkspaceId" :options="workspaceOptions" @select="handleWorkspaceSelect" />
    </template>

    <template #aside="{ Header }">
      <component :is="Header">
        <el-tabs class="w-full" v-model="targetType" @tab-change="handleTargetTypeChange">
          <el-tab-pane label="按用户组" name="user-group" />
          <el-tab-pane label="按用户" name="user" />
        </el-tabs>
      </component>

      <UserGroupAuthorizationList v-if="targetType === 'user-group'" :active-id="selectedUserGroupId" :user-groups="userGroups" @select="handleUserGroupSelect" />
      <UserAuthorizationList v-else :active-id="selectedUserId" :users="workspaceMembers" @select="handleUserSelect" />
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <div class="w-full">
          <h4 class="mb-4">资源权限配置</h4>
          <el-tabs v-model="resourceType" class="w-full" @tab-change="loadResourcePermissions">
            <el-tab-pane v-for="resourceTypeOption in resourceTypeOptions" :key="resourceTypeOption.value" :label="resourceTypeOption.label" :name="resourceTypeOption.value" />
          </el-tabs>
        </div>
      </component>

      <PermissionTable v-loading="loadingPermissions" :data="resourcePermissions" :resource-type="resourceType" @submit="handlePermissionsSubmit" />
    </template>
  </MkViewLayout>
</template>
