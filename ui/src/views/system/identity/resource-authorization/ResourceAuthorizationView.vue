<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import WorkspaceApi from '@/api/admin/system/workspace'
import CommonSystemApi from '@/api/admin/system/common'
import ResourceAuthorizationApi from '@/api/admin/system/resource-authorization'
import { RESOURCE_TYPE, RESOURCE_PERMISSION } from '@/api/enums'
import type {
  ResourceAuthorizationType,
  ResourcePermissionItem,
  ResourcePermissionPayload,
  WorkspaceMemberOption,
  WorkspaceItem,
} from '@/api/types'
import { perm } from '@/permission'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'
import PermissionTable from './components/PermissionTable.vue'
import { RESOURCE_AUTHORIZATION_LABELS } from './constants'

const route = useRoute()
const { auth } = useStore()

const resourceType = computed<ResourceAuthorizationType>(
  () => route.meta.resource ?? RESOURCE_TYPE.APPLICATION,
)
const resourceLabel = computed(() => RESOURCE_AUTHORIZATION_LABELS[resourceType.value])
const canEditPermissions = computed(() => {
  const permissionKey = resourceType.value.toLowerCase() as Lowercase<ResourceAuthorizationType>
  return perm.authorization[permissionKey].edit()
})

/* 工作空间与成员 */
const loadingView = ref(false)
const loadingMembers = ref(false)
const workspaceOptions = ref<WorkspaceItem[]>([])
const selectedWorkspaceId = ref('default')
const workspaceMembers = ref<WorkspaceMemberOption[]>([])
const selectedMemberId = ref('')

function loadWorkspaceOptions() {
  loadingView.value = true
  return WorkspaceApi.getSystemWorkspaceList()
    .then((workspaces) => {
      workspaceOptions.value = workspaces
      if (!workspaces.some(({ id }) => id === selectedWorkspaceId.value)) {
        selectedWorkspaceId.value = workspaces[0]?.id ?? 'default'
      }
      return loadWorkspaceMembers()
    })
    .finally(() => {
      loadingView.value = false
    })
}

function loadWorkspaceMembers(preferredMemberId?: string) {
  loadingMembers.value = true
  return CommonSystemApi.getWorkspaceMembers(selectedWorkspaceId.value)
    .then((members) => {
      workspaceMembers.value = members
      const memberId = preferredMemberId ?? selectedMemberId.value
      selectedMemberId.value = members.some(({ id }) => id === memberId)
        ? memberId
        : (members[0]?.id ?? '')
      return loadResourcePermissions()
    })
    .finally(() => {
      loadingMembers.value = false
    })
}

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
  selectedMemberId.value = ''
  loadWorkspaceMembers()
}

function handleMemberSelect(member: WorkspaceMemberOption) {
  selectedMemberId.value = member.id
  loadResourcePermissions()
}

function getMemberRoleText(member: WorkspaceMemberOption) {
  return member.roles?.join('，') ?? ''
}

/* 资源权限 */
const loadingPermissions = ref(false)
const savingPermissions = ref(false)
const resourcePermissions = ref<ResourcePermissionItem[]>([])

function buildResourceTree(resourceItems: ResourcePermissionItem[]) {
  if (resourceType.value === RESOURCE_TYPE.MODEL) return resourceItems

  const resourceMap = new Map(
    resourceItems.map((resource) => [
      resource.id,
      {
        ...resource,
        children: [] as ResourcePermissionItem[],
        permission:
          resource.resource_type === 'folder' &&
          resource.folder_id === null &&
          resource.permission === RESOURCE_PERMISSION.NOT_AUTH
            ? RESOURCE_PERMISSION.VIEW
            : resource.permission,
      },
    ]),
  )

  resourceMap.forEach((resource) => {
    if (!resource.folder_id) return
    resourceMap.get(resource.folder_id)?.children?.push(resource)
  })

  return [...resourceMap.values()].filter(
    ({ folder_id }) => !folder_id || !resourceMap.has(folder_id),
  )
}

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

function handlePermissionsSubmit(permissions: ResourcePermissionPayload[]) {
  if (!selectedMemberId.value) return

  savingPermissions.value = true
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
      savingPermissions.value = false
    })
}

watch(resourceType, () => loadResourcePermissions())
onMounted(() => loadWorkspaceOptions())
</script>

<template>
  <MkViewLayout class="system-resource-authorization" :loading="loadingView">
    <template #top>
      <div class="flex items-center gap-4">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>资源授权</el-breadcrumb-item>
          <el-breadcrumb-item>{{ resourceLabel }}</el-breadcrumb-item>
        </el-breadcrumb>
        <el-divider v-if="auth.isEE" direction="vertical" />
        <WorkspaceDropdown
          v-if="auth.isEE"
          v-model="selectedWorkspaceId"
          :options="workspaceOptions"
          @select="handleWorkspaceSelect"
        />
      </div>
    </template>

    <template #aside="{ Header }">
      <component :is="Header">
        <h4>成员</h4>
      </component>
      <MkSearchList
        v-loading="loadingMembers"
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
        <h4>{{ resourceLabel }}权限配置</h4>
      </component>
      <PermissionTable
        v-if="selectedMemberId"
        v-loading="loadingPermissions || savingPermissions"
        :allow-role="auth.isEE || auth.isPE"
        :data="resourcePermissions"
        :editable="canEditPermissions"
        :resource-type="resourceType"
        @submit="handlePermissionsSubmit"
      />
      <MkEmpty v-else description="当前工作空间暂无成员" class="mt-20" />
    </template>
  </MkViewLayout>
</template>
