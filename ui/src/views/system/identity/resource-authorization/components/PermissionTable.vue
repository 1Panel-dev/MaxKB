<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import ProviderApi from '@/api/admin/workspace/model/provider'
import { RESOURCE_TYPE, RESOURCE_PERMISSION } from '@/api/enums'
import type {
  ModelProviderItem,
  OptionItem,
  RequestParams,
  ResourceAuthorizationType,
  ResourcePermission,
  ResourcePermissionItem,
  ResourcePermissionPayload,
} from '@/api/types'
import { resetUrl } from '@/utils/common'
import { getPermissionOptions } from '../constants'
import BatchSetPermissionDialog from '../dialog/BatchSetPermissionDialog.vue'

defineOptions({ name: 'ResourcePermissionTable' })

const props = defineProps<{
  data: ResourcePermissionItem[]
  resourceType: ResourceAuthorizationType
}>()
const emit = defineEmits<{
  submit: [permissions: ResourcePermissionPayload[]]
}>()

const permissionSearchFields = computed<OptionItem<string>[]>(() => [
  { label: '名称', value: 'name' },
  {
    label: '权限',
    multiple: true,
    options: getPermissionOptions(),
    value: 'permission',
  },
])

/* 搜索与展开 */
const searchQuery = ref<RequestParams>()
function handleSearch(query?: RequestParams) {
  searchQuery.value = query
}

function filterResourceTree(resources: ResourcePermissionItem[]): ResourcePermissionItem[] {
  const name = typeof searchQuery.value?.name === 'string' ? searchQuery.value.name.trim() : ''
  const permissions = searchQuery.value?.permission as ResourcePermission[] | undefined
  if (!name && !permissions?.length) return resources

  return resources.flatMap((resource) => {
    const children = filterResourceTree(resource.children ?? [])
    const matchesName = name
      ? resource.name.toLocaleLowerCase().includes(name.toLocaleLowerCase())
      : true
    const matchesPermission = permissions?.length ? permissions.includes(resource.permission) : true

    return (matchesName && matchesPermission) || children.length ? [{ ...resource, children }] : []
  })
}

const filteredResources = computed(() => filterResourceTree(props.data))
const expandedResourceIds = computed(() => {
  if (!searchQuery.value) return props.data[0]?.id ? [props.data[0].id] : []

  const folderIds: string[] = []
  const collectFolderIds = (resources: ResourcePermissionItem[]) => {
    resources.forEach((resource) => {
      if (resource.children?.length) {
        folderIds.push(resource.id)
        collectFolderIds(resource.children)
      }
    })
  }
  collectFolderIds(filteredResources.value)
  return folderIds
})

/* 权限选项 */

function flattenResources(resources: ResourcePermissionItem[]): ResourcePermissionItem[] {
  return resources.flatMap((resource) => [resource, ...flattenResources(resource.children ?? [])])
}

function collectUnauthorizedAncestors(folderId: string | null) {
  const ancestors: ResourcePermissionItem[] = []
  const flattenedResources = flattenResources(props.data)
  let currentFolderId = folderId

  while (currentFolderId) {
    const parent = flattenedResources.find(({ id }) => id === currentFolderId)
    if (!parent) break
    if (parent.permission === RESOURCE_PERMISSION.NOT_AUTH) ancestors.push(parent)
    currentFolderId = parent.folder_id
  }

  return ancestors
}

function buildPermissionPayload(permission: ResourcePermission, resource: ResourcePermissionItem) {
  const payloadMap = new Map<string, ResourcePermissionPayload>([
    [resource.id, { permission, target_id: resource.id }],
  ])

  if (permission === RESOURCE_PERMISSION.NOT_AUTH && resource.resource_type === 'folder') {
    flattenResources(resource.children ?? []).forEach(({ id }) => {
      payloadMap.set(id, { permission: RESOURCE_PERMISSION.NOT_AUTH, target_id: id })
    })
  } else if (permission !== RESOURCE_PERMISSION.NOT_AUTH) {
    collectUnauthorizedAncestors(resource.folder_id).forEach(({ id }) => {
      payloadMap.set(id, { permission: RESOURCE_PERMISSION.VIEW, target_id: id })
    })
  }

  return payloadMap
}

function handlePermissionChange(permission: ResourcePermission, resource: ResourcePermissionItem) {
  emit('submit', [...buildPermissionPayload(permission, resource).values()])
}

/* 批量授权 */
const tableRef = ref<{ clearSelection: () => void }>()
const batchSelectedResources = ref<ResourcePermissionItem[]>([])

function handleSelectionChange(selection: unknown[]) {
  batchSelectedResources.value = selection as ResourcePermissionItem[]
}

const batchPermissionDialogRef = useTemplateRef<InstanceType<typeof BatchSetPermissionDialog>>(
  'batchPermissionDialogRef',
)

function handleOpenBatchDialog() {
  batchPermissionDialogRef.value?.open()
}

function handleBatchSubmit(permission: ResourcePermission) {
  const payloadMap = new Map<string, ResourcePermissionPayload>()
  batchSelectedResources.value.forEach((resource) => {
    buildPermissionPayload(permission, resource).forEach((payload, id) => {
      payloadMap.set(id, payload)
    })
  })
  emit('submit', [...payloadMap.values()])
  tableRef.value?.clearSelection()
  batchSelectedResources.value = []
}

/* 模型供应商图标 */
const modelProviders = ref<ModelProviderItem[]>([])
function getModelProviderIcon(resource: ResourcePermissionItem) {
  return modelProviders.value.find(({ provider }) => provider === resource.icon)?.icon ?? ''
}

watch(
  () => props.resourceType,
  (resourceType) => {
    if (resourceType !== RESOURCE_TYPE.MODEL || modelProviders.value.length) return
    ProviderApi.getProviderList().then((providers) => {
      modelProviders.value = providers
    })
  },
  { immediate: true },
)
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <div class="mb-4 flex-between">
      <el-button
        type="primary"
        :disabled="batchSelectedResources.length === 0"
        @click="handleOpenBatchDialog"
      >
        <MkIcon name="icon-lock" />
        <span>配置权限</span>
      </el-button>
      <MkComplexSearch :fields="permissionSearchFields" @change="handleSearch" />
    </div>

    <MkTable
      ref="tableRef"
      :data="filteredResources"
      :expand-row-keys="expandedResourceIds"
      :max-table-height="300"
      show-overflow-tooltip
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="40" reserve-selection />
      <el-table-column class-name="resource-name-column" label="名称" min-width="260" prop="name">
        <template #default="{ row }: { row: ResourcePermissionItem }">
          <div class="flex min-w-0 items-center gap-2">
            <MkIcon
              v-if="row.resource_type === 'folder'"
              name="icon_file-folder_colorful"
              :size="18"
            />
            <span
              v-else-if="resourceType === RESOURCE_TYPE.MODEL"
              class="block h-5 w-5 shrink-0"
              :innerHTML="getModelProviderIcon(row)"
            />
            <ToolIcon
              v-else-if="resourceType === RESOURCE_TYPE.TOOL"
              :icon="row.icon ?? undefined"
              :size="20"
              :type="row.tool_type ?? undefined"
            />

            <el-avatar
              v-else-if="resourceType === RESOURCE_TYPE.APPLICATION"
              class="bg-transparent!"
              shape="square"
              :size="20"
            >
              <img :src="resetUrl(row?.icon, true)" />
            </el-avatar>
            <span class="min-w-0 truncate" :title="row.name">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作权限" width="450">
        <template #default="{ row }: { row: ResourcePermissionItem }">
          <el-radio-group
            :model-value="row.permission"
            @change="handlePermissionChange($event as ResourcePermission, row)"
          >
            <template
              v-for="permissionOption in getPermissionOptions()"
              :key="permissionOption.value"
            >
              <el-radio :value="permissionOption.value">{{ permissionOption.label }}</el-radio>
            </template>
          </el-radio-group>
        </template>
      </el-table-column>
    </MkTable>

    <BatchSetPermissionDialog ref="batchPermissionDialogRef" @submit="handleBatchSubmit" />
  </div>
</template>

<style scoped lang="scss">
:deep(.resource-name-column .cell) {
  align-items: center;
  display: flex;
}
</style>
