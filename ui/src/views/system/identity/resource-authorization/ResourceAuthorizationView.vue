<script setup lang="ts">
import { onMounted, ref } from 'vue'
import WorkspaceApi from '@/api/admin/system/workspace'
import CommonSystemApi from '@/api/admin/system/common'
import ResourceAuthorizationApi from '@/api/admin/system/resource-authorization'
import { RESOURCE_TYPE, RESOURCE_PERMISSION } from '@/api/enums'
import type {
  ResourceAuthorizationType,
  ResourcePermissionItem,
  ResourcePermissionPayload,
  CommonUserOption,
  WorkspaceItem,
} from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'
import PermissionTable from './components/PermissionTable.vue'

const { auth } = useStore()

const resourceType = ref<ResourceAuthorizationType>(RESOURCE_TYPE.APPLICATION)

/* 选择工作空间列表 */
const loadingView = ref(false)
const selectedWorkspaceId = ref('default')
const workspaceOptions = ref<WorkspaceItem[]>([])

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
  loadWorkspaceMembers()
}

function loadWorkspaceOptions() {
  return WorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
    workspaceOptions.value = workspaces
  })
}

/* 选择用户（普通用户） */

const workspaceMembers = ref<CommonUserOption[]>([])
const selectedMemberId = ref('')

function loadWorkspaceMembers() {
  return CommonSystemApi.getWorkspaceMembers(selectedWorkspaceId.value).then((members) => {
    workspaceMembers.value = members
    selectedMemberId.value = members[0]?.id ?? ''
    return loadResourcePermissions()
  })
}

function handleMemberSelect(member: CommonUserOption) {
  selectedMemberId.value = member.id
  loadResourcePermissions()
}

function getMemberRoleText(member: CommonUserOption) {
  return member.roles?.join('，') ?? ''
}

/* 资源权限 */
const loadingPermissions = ref(false)
const resourcePermissions = ref<ResourcePermissionItem[]>([])

function loadResourcePermissions() {
  if (!selectedMemberId.value) {
    resourcePermissions.value = []
    return Promise.resolve()
  }

  loadingPermissions.value = true
  return ResourceAuthorizationApi.getUserResourcePermissions(
    selectedWorkspaceId.value,
    selectedMemberId.value,
    resourceType.value,
  )
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
    permission:
      !resource.folder_id && resource.permission === RESOURCE_PERMISSION.NOT_AUTH
        ? RESOURCE_PERMISSION.VIEW
        : resource.permission,
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
  if (!selectedMemberId.value) return

  loadingPermissions.value = true
  ResourceAuthorizationApi.putUserResourcePermissions(
    selectedWorkspaceId.value,
    selectedMemberId.value,
    resourceType.value,
    permissions,
  )
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
  Promise.all(
    auth.isEE ? [loadWorkspaceOptions(), loadWorkspaceMembers()] : [loadWorkspaceMembers()],
  ).finally(() => {
    loadingView.value = false
  })
})
</script>

<template>
  <MkViewLayout class="system-resource-authorization" :loading="loadingView">
    <template #top v-if="auth.isEE">
      <WorkspaceDropdown
        v-model="selectedWorkspaceId"
        :options="workspaceOptions"
        @select="handleWorkspaceSelect"
      />
    </template>

    <template #aside="{ Header }">
      <component :is="Header">
        <h4>按用户</h4>
      </component>
      <MkSearchList
        :data="workspaceMembers"
        :default-active="selectedMemberId"
        :props="{ label: 'nick_name', value: 'id' }"
        @click="handleMemberSelect"
      >
        <template #default="{ row }">
          <div class="flex min-w-0 flex-1 items-center gap-2">
            <span class="min-w-0 truncate" :title="row.nick_name">{{ row.nick_name }}</span>
            <span
              v-if="(auth.isEE || auth.isPE) && row.roles?.length"
              class="min-w-0 truncate text-N600"
              :title="getMemberRoleText(row)"
            >
              ({{ getMemberRoleText(row) }})
            </span>
          </div>
        </template>
      </MkSearchList>
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4>资源权限配置</h4>
      </component>
      <PermissionTable
        v-loading="loadingPermissions"
        :data="resourcePermissions"
        :resource-type="resourceType"
        @submit="handlePermissionsSubmit"
      />
    </template>
  </MkViewLayout>
</template>
