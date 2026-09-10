<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type RelatedResourcesApi from '@/api/admin/workspace/related-resources'
import ModelProviderApi from '@/api/admin/model-provider'
import WorkspaceApi from '@/api/admin/system/workspace'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import type { Dict, ModelProviderItem, OptionItem, RelatedResource, ResourceType } from '@/api/types'
import ResourceIcon from './ResourceIcon.vue'
import type { RelatedResourceTarget } from './types'

defineOptions({ name: 'RelatedResourcesDrawer' })
const props = defineProps<{
  api: typeof RelatedResourcesApi
  showWorkspace?: boolean
}>()
const emit = defineEmits<{ closed: [] }>()

/* 当前资源与展示配置 */
const visible = ref(false)
const resourceType = ref<ResourceType>(RESOURCE_TYPE.APPLICATION)
const targetResource = ref<RelatedResourceTarget>()
const resourceLabels = {
  [RESOURCE_TYPE.APPLICATION]: '智能体',
  [RESOURCE_TYPE.KNOWLEDGE]: '知识库',
  [RESOURCE_TYPE.TOOL]: '工具',
  [RESOURCE_TYPE.MODEL]: '模型',
}
const resourceTypeOptions = Object.entries(resourceLabels).map(([value, label]) => ({ value, label }))
const searchFields = [
  { label: '名称', value: 'resource_name' },
  { label: '创建者', value: 'user_name' },
  { label: '类型', value: 'resource_type', multiple: true, options: resourceTypeOptions },
]
const relationTabs = [
  { value: 'dependency', label: '依赖' },
  { value: 'dependent', label: '被依赖' },
]
const relationDirection = ref<'dependency' | 'dependent'>('dependency')

/* 分页查询：两个关系方向共用表格，仅转换关系字段。 */
const loading = ref(false)
const relatedResources = ref<RelatedResource[]>([])
const resourceRows = computed(() =>
  relatedResources.value.map((resource) => ({
    ...resource,
    resourceId: relationDirection.value === 'dependency' ? resource.target_id : resource.source_id,
    resourceType: relationDirection.value === 'dependency' ? resource.target_type : resource.source_type,
  })),
)
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<Dict<unknown>>({})

function loadResources() {
  if (!visible.value || !targetResource.value) return
  const isDependency = relationDirection.value === 'dependency'
  const { resource_type, ...query } = searchQuery.value
  if (resource_type) query[isDependency ? 'target_type' : 'source_type'] = resource_type
  if (selectedWorkspaceIds.value.length) query.workspace_ids = JSON.stringify(selectedWorkspaceIds.value)
  const request = isDependency ? props.api.getResourceDependencies : props.api.getResourceDependents
  loading.value = true
  return request(targetResource.value.workspace_id, resourceType.value, targetResource.value.id, { ...pagination.value }, query)
    .then((page) => {
      relatedResources.value = page.records
      pagination.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function searchResources(query?: Dict<unknown>) {
  searchQuery.value = query ?? {}
  pagination.value.currentPage = 1
  loadResources()
}

function changeDirection() {
  searchQuery.value = {}
  selectedWorkspaceIds.value = []
  relatedResources.value = []
  pagination.value = { currentPage: 1, pageSize: 20, total: 0 }
  loadResources()
}

/* 工作空间筛选：确认或重置后从第一页查询。 */
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedWorkspaceIds = ref<string[]>([])
function handleWorkspaceFilterChange() {
  pagination.value.currentPage = 1
  loadResources()
}

/* 抽屉生命周期：资源切换及关闭后使旧请求失效。 */
const providers = ref<ModelProviderItem[]>([])

function open(type: ResourceType, resource: RelatedResourceTarget) {
  resourceType.value = type
  targetResource.value = cloneDeep(resource)
  relationDirection.value =
    type === RESOURCE_TYPE.MODEL || (type === RESOURCE_TYPE.TOOL && resource.tool_type !== TOOL_TYPE.WORKFLOW) ? 'dependent' : 'dependency'
  visible.value = true
  loadResources()
  if (!providers.value.length) {
    ModelProviderApi.getProviderList().then((result) => {
      providers.value = result
    })
  }
  if (props.showWorkspace) {
    WorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
      workspaceOptions.value = workspaces.flatMap(({ id, name }) => (id ? [{ value: id, label: name }] : []))
    })
  }
}
function close() {
  visible.value = false
}
function handleClosed() {
  if (visible.value) return
  resetData()
  emit('closed')
}

function resetData() {
  loading.value = false
  targetResource.value = undefined
  relatedResources.value = []
  pagination.value = { currentPage: 1, pageSize: 20, total: 0 }
  searchQuery.value = {}
  relationDirection.value = 'dependency'
  workspaceOptions.value = []
  selectedWorkspaceIds.value = []
}
onBeforeUnmount(resetData)
defineExpose({ open, close })
</script>

<template>
  <MkDrawer v-model="visible" title="查看关联资源" size="60%" @closed="handleClosed">
    <template v-if="targetResource">
      <div class="flex items-center mb-4">
        <span class="mr-4 mk-N600!">{{ resourceLabels[resourceType] }}</span>

        <ResourceIcon
          :resource-type="resourceType"
          :type="targetResource.tool_type ?? targetResource.type"
          :icon="targetResource.icon"
          :provider="targetResource.provider"
          :providers="providers"
        />
        <span class="ml-2">{{ targetResource.name }}</span>
      </div>

      <h4 class="mk-title-decoration mb-4">关联资源</h4>

      <div class="flex-between gap-3">
        <el-radio-group v-model="relationDirection" @change="changeDirection">
          <el-radio-button v-for="tab in relationTabs" :key="tab.value" :value="tab.value">{{ tab.label }}</el-radio-button>
        </el-radio-group>
        <MkComplexSearch :fields="searchFields" @change="searchResources" />
      </div>
      <MkTable
        v-model:pagination-config="pagination"
        v-loading="loading"
        class="mt-4"
        :data="resourceRows"
        :max-table-height="340"
        row-key="resourceId"
        @current-change="loadResources"
        @size-change="loadResources"
      >
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <!-- // TODO: 资源跳转 -->
            <div class="flex items-center gap-2">
              <ResourceIcon :resource-type="row.resourceType" :type="row.type" :icon="row.icon" :providers="providers" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="desc" label="描述" min-width="160" show-overflow-tooltip />
        <el-table-column label="类型" min-width="100">
          <template #default="{ row }">{{ resourceLabels[row.resourceType as ResourceType] }}</template>
        </el-table-column>
        <el-table-column v-if="showWorkspace" prop="workspace_name" label="工作空间" min-width="140" show-overflow-tooltip>
          <template #header>
            <!-- 筛选关联资源所属工作空间 -->
            <MkTableFilter v-model="selectedWorkspaceIds" label="工作空间" :options="workspaceOptions" @change="handleWorkspaceFilterChange" />
          </template>
        </el-table-column>
        <el-table-column prop="username" label="创建者" min-width="100" show-overflow-tooltip />
      </MkTable>
    </template>
  </MkDrawer>
</template>
