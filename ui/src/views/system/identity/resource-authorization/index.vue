<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type {
  CommonUserOption,
  OptionItem,
  ResourceAuthorizationType,
  ResourcePermissionItem,
  ResourcePermissionPayload,
  SystemUserGroup,
  WorkspaceItem,
} from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import CommonSystemApi from '@/api/admin/system/common'
import ResourceAuthorizationApi from '@/api/admin/system/resource-authorization'
import UserGroupsApi from '@/api/admin/system/user-groups'
import WorkspaceApi from '@/api/admin/system/workspace'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import PermissionTable from './components/PermissionTable.vue'
import UserAuthorizationList from './components/UserAuthorizationList.vue'
import UserGroupAuthorizationList from './components/user-group/UserGroupAuthorizationList.vue'
import { RESOURCE_AUTHORIZATION_MESSAGE_KEYS } from './constants'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import { perm } from '@/permission'

const { auth, user } = useStore()
const { t, te } = useI18n({ useScope: 'global' })
const route = useRoute()
const pageTitle = computed(() => {
  const title = route.meta.title ?? ''
  return te(title) ? t(title) : title
})

const resourceType = ref<ResourceAuthorizationType>((route.meta.resource as ResourceAuthorizationType) ?? RESOURCE_TYPE.APPLICATION)
const resourceReadPermissions: Record<ResourceAuthorizationType, () => boolean> = {
  [RESOURCE_TYPE.APPLICATION]: perm.system.authorization.application.read,
  [RESOURCE_TYPE.KNOWLEDGE]: perm.system.authorization.knowledge.read,
  [RESOURCE_TYPE.TOOL]: perm.system.authorization.tool.read,
  [RESOURCE_TYPE.MODEL]: perm.system.authorization.model.read,
}

const resourceTypeOptions = computed<OptionItem<ResourceAuthorizationType>[]>(() =>
  [RESOURCE_TYPE.APPLICATION, RESOURCE_TYPE.KNOWLEDGE, RESOURCE_TYPE.TOOL, RESOURCE_TYPE.MODEL]
    .filter((value) => resourceReadPermissions[value]())
    .map((value) => ({
      label: t(RESOURCE_AUTHORIZATION_MESSAGE_KEYS[value]),
      value,
    })),
)

/* 选择工作空间列表 */
const loadingView = ref(false)
const selectedWorkspaceId = ref(user.userInfo?.workspace_list?.[0]?.id ?? 'default')
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
const loadingUsers = ref(false)
const selectedUserGroupId = ref('')
const selectedUserId = ref('')

function loadAuthorizationTargets() {
  return Promise.all([
    UserGroupsApi.getSystemUserGroups(selectedWorkspaceId.value),
    CommonSystemApi.getWorkspaceMembers(selectedWorkspaceId.value),
  ]).then(([groups, users]) => {
    userGroups.value = groups
    workspaceMembers.value = users
    selectedUserGroupId.value = groups[0]?.id ?? ''
    selectedUserId.value = users[0]?.id ?? ''
    return loadResourcePermissions()
  })
}

// 用户搜索只更新候选列表，保留当前授权对象和权限编辑状态。
function handleUserSearch(keyword: string) {
  if (loadingUsers.value) return

  loadingUsers.value = true
  CommonSystemApi.getWorkspaceMembers(selectedWorkspaceId.value, keyword ? { nick_name: keyword } : undefined)
    .then((users) => {
      workspaceMembers.value = users
    })
    .finally(() => {
      loadingUsers.value = false
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
    loadingPermissions.value = false
    return Promise.resolve()
  }

  loadingPermissions.value = true
  const permissionRequest =
    targetType.value === 'user-group'
      ? ResourceAuthorizationApi.getUserGroupResourcePermissions(selectedWorkspaceId.value, targetId, resourceType.value)
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
  }))
  const resourceMap = new Map(resources.map((resource) => [resource.id, resource]))

  resources.forEach((resource) => {
    if (!resource.folder_id) return

    const parentResource = resourceMap.get(resource.folder_id)
    if (parentResource) {
      parentResource.children.push(resource)
    }
  })

  // 根目录仅作为资源容器，授权列表直接展示其子目录和资源。
  return resources.filter(({ folder_id }) => !folder_id).flatMap((resource) => (resource.resource_type === 'folder' ? resource.children : [resource]))
}

/* 保存权限 */

function handlePermissionsSubmit(permissions: ResourcePermissionPayload[]) {
  if (!canEditResourcePermission.value || loadingPermissions.value) return

  const targetId = targetType.value === 'user-group' ? selectedUserGroupId.value : selectedUserId.value

  if (!targetId) return

  loadingPermissions.value = true
  const permissionRequest =
    targetType.value === 'user-group'
      ? ResourceAuthorizationApi.putUserGroupResourcePermissions(selectedWorkspaceId.value, targetId, resourceType.value, permissions)
      : ResourceAuthorizationApi.putUserResourcePermissions(selectedWorkspaceId.value, targetId, resourceType.value, permissions)

  permissionRequest
    .then(() => {
      MsgSuccess(t('common.messages.submitSuccess'))
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

// 权限
const resourceEditPermissions: Record<ResourceAuthorizationType, () => boolean> = {
  [RESOURCE_TYPE.APPLICATION]: perm.system.authorization.application.edit,
  [RESOURCE_TYPE.KNOWLEDGE]: perm.system.authorization.knowledge.edit,
  [RESOURCE_TYPE.TOOL]: perm.system.authorization.tool.edit,
  [RESOURCE_TYPE.MODEL]: perm.system.authorization.model.edit,
}
const canEditResourcePermission = computed(() => resourceEditPermissions[resourceType.value]())
</script>

<template>
  <MkViewLayout :title="pageTitle" class="system-resource-authorization" :loading="loadingView">
    <template #top v-if="auth.isEE">
      <WorkspaceDropdown v-model="selectedWorkspaceId" :options="workspaceOptions" @select="handleWorkspaceSelect" />
    </template>

    <template #aside="{ Header }">
      <component :is="Header">
        <el-tabs class="w-full" v-model="targetType" @tab-change="handleTargetTypeChange">
          <el-tab-pane :label="t('resource.authorization.byGroup')" name="user-group" />
          <el-tab-pane :label="t('resource.authorization.byUser')" name="user" />
        </el-tabs>
      </component>

      <UserGroupAuthorizationList
        v-if="targetType === 'user-group'"
        :active-id="selectedUserGroupId"
        :user-groups="userGroups"
        @select="handleUserGroupSelect"
      />
      <UserAuthorizationList
        v-else
        :key="selectedWorkspaceId"
        v-loading="loadingUsers"
        :inert="loadingUsers"
        :active-id="selectedUserId"
        :users="workspaceMembers"
        @select="handleUserSelect"
        @search="handleUserSearch"
      />
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <div class="w-full">
          <h4 class="mb-4">{{ t('resource.authorization.permissionTitle') }}</h4>
          <el-tabs v-model="resourceType" class="w-full" @tab-change="loadResourcePermissions">
            <el-tab-pane
              v-for="resourceTypeOption in resourceTypeOptions"
              :key="resourceTypeOption.value"
              :label="resourceTypeOption.label"
              :name="resourceTypeOption.value"
            />
          </el-tabs>
        </div>
      </component>
      <div v-loading="loadingPermissions">
        <PermissionTable
          :data="resourcePermissions"
          :resource-type="resourceType"
          :disabled="!canEditResourcePermission"
          @submit="handlePermissionsSubmit"
        />
      </div>
    </template>
  </MkViewLayout>
</template>
