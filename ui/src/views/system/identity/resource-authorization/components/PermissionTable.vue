<script setup lang="ts">
import { computed, ref, watch } from 'vue'
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

defineOptions({ name: 'ResourcePermissionTable' })

const props = defineProps<{
  allowRole: boolean
  data: ResourcePermissionItem[]
  editable: boolean
  resourceType: ResourceAuthorizationType
}>()
const emit = defineEmits<{
  submit: [permissions: ResourcePermissionPayload[]]
}>()

const permissionSearchFields = computed<OptionItem<string>[]>(() => [
  { label: '名称', value: 'name' },
  {
    label: '权限',
    options: getPermissionOptions({ allowRole: props.allowRole }),
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
  const permission = searchQuery.value?.permission as ResourcePermission | undefined
  if (!name && !permission) return resources

  return resources.flatMap((resource) => {
    const children = filterResourceTree(resource.children ?? [])
    const matchesName = name
      ? resource.name.toLocaleLowerCase().includes(name.toLocaleLowerCase())
      : true
    const matchesPermission = permission ? resource.permission === permission : true

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
function getRowPermissionOptions(resource: ResourcePermissionItem) {
  const isFolder = resource.resource_type === 'folder'
  return getPermissionOptions({
    allowRole: props.allowRole,
    isFolder,
    isRootFolder: isFolder && resource.folder_id === null,
  })
}

const selectedResources = ref<ResourcePermissionItem[]>([])
const tableRef = ref<{ clearSelection: () => void }>()
const batchPermissionOptions = computed(() => {
  const hasRootFolder = selectedResources.value.some(
    ({ folder_id, resource_type }) => resource_type === 'folder' && folder_id === null,
  )
  const hasFolder = selectedResources.value.some(({ resource_type }) => resource_type === 'folder')
  return getPermissionOptions({
    allowRole: props.allowRole,
    isFolder: hasFolder,
    isRootFolder: hasRootFolder,
  })
})

function handleSelectionChange(selection: unknown[]) {
  selectedResources.value = selection as ResourcePermissionItem[]
}

/* 单项授权的目录级联 */
function collectDescendants(resource: ResourcePermissionItem): ResourcePermissionItem[] {
  return (resource.children ?? []).flatMap((child) => [child, ...collectDescendants(child)])
}

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
    collectDescendants(resource).forEach(({ id }) => {
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
const batchDialogVisible = ref(false)
const batchPermission = ref<ResourcePermission>()

function resetBatchDialog() {
  batchPermission.value = undefined
}

function handleOpenBatchDialog() {
  if (selectedResources.value.length) batchDialogVisible.value = true
}

function handleCloseBatchDialog() {
  batchDialogVisible.value = false
  resetBatchDialog()
}

function handleBatchSubmit() {
  if (!batchPermission.value) return

  const payloadMap = new Map<string, ResourcePermissionPayload>()
  selectedResources.value.forEach((resource) => {
    buildPermissionPayload(batchPermission.value!, resource).forEach((payload, id) => {
      payloadMap.set(id, payload)
    })
  })
  emit('submit', [...payloadMap.values()])
  tableRef.value?.clearSelection()
  selectedResources.value = []
  handleCloseBatchDialog()
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
    <div class="mb-4 flex justify-end">
      <MkComplexSearch :fields="permissionSearchFields" @change="handleSearch" />
    </div>

    <MkTable
      ref="tableRef"
      :data="filteredResources"
      :expand-row-keys="expandedResourceIds"
      :max-table-height="250"
      show-overflow-tooltip
      @selection-change="handleSelectionChange"
    >
      <el-table-column v-if="editable" type="selection" width="48" reserve-selection />
      <el-table-column label="名称" min-width="260" prop="name">
        <template #default="{ row }: { row: ResourcePermissionItem }">
          <div class="flex min-w-0 items-center gap-2">
            <MkIcon
              v-if="row.resource_type === 'folder'"
              name="icon_file-folder_colorful"
              :size="20"
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
              v-else-if="resourceType === RESOURCE_TYPE.APPLICATION && row.icon"
              class="bg-transparent!"
              shape="square"
              :size="20"
            >
              <img :src="resetUrl(row.icon)" alt="" />
            </el-avatar>
            <MkIcon
              v-else
              :name="
                resourceType === RESOURCE_TYPE.KNOWLEDGE
                  ? 'icon_book_filled'
                  : 'icon_robot_filled'
              "
              :size="20"
              class="text-primary!"
            />
            <span class="min-w-0 truncate" :title="row.name">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="权限" min-width="360">
        <template #default="{ row }: { row: ResourcePermissionItem }">
          <el-radio-group
            :disabled="!editable"
            :model-value="row.permission"
            @change="handlePermissionChange($event as ResourcePermission, row)"
          >
            <el-radio
              v-for="permissionOption in getRowPermissionOptions(row)"
              :key="permissionOption.value"
              :value="permissionOption.value"
            >
              {{ permissionOption.label }}
            </el-radio>
          </el-radio-group>
        </template>
      </el-table-column>

      <template #footer-batch-actions>
        <el-button type="primary" @click="handleOpenBatchDialog">配置权限</el-button>
      </template>
    </MkTable>

    <MkDialog v-model="batchDialogVisible" title="配置权限" width="480" @closed="resetBatchDialog">
      <el-radio-group v-model="batchPermission" class="flex! flex-col! items-stretch! gap-3">
        <el-radio
          v-for="permissionOption in batchPermissionOptions"
          :key="permissionOption.value"
          :value="permissionOption.value"
          class="m-0! h-auto! items-start!"
        >
          <div>
            <p>{{ permissionOption.label }}</p>
            <p v-if="permissionOption.description" class="text-N600">
              {{ permissionOption.description }}
            </p>
          </div>
        </el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="handleCloseBatchDialog">取消</el-button>
        <el-button type="primary" :disabled="!batchPermission" @click="handleBatchSubmit">
          确认
        </el-button>
      </template>
    </MkDialog>
  </div>
</template>
