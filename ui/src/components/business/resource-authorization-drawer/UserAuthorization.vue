<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { RESOURCE_PERMISSION } from '@/api/enums'
import { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'
import type { Dict, ResourceAuthorizationTargetType, ResourcePermission, ResourceUserPermission } from '@/api/types'
import MkTable from '@/components/global/mk-table/index.vue'
import { useStore } from '@/stores'
import type ResourceAuthorizationApi from '@/api/admin/workspace/resource-authorization'
import type SystemResourceAuthorizationApi from '@/api/admin/system/resource-management/resource-authorization'
import type { ResourcePermissionOption } from './types'

const props = defineProps<{
  api: typeof ResourceAuthorizationApi | typeof SystemResourceAuthorizationApi
  workspaceId: string
  targetId: string
  type: ResourceAuthorizationTargetType
  submitting: boolean
  permissionOptions: ResourcePermissionOption[]
}>()
const emit = defineEmits<{ configure: [subjectIds: string[], permission?: ResourcePermission] }>()

/* 根目录不提供“不授权”，按“查看”展示接口返回的该权限。 */
const canSelectNotAuth = computed(() => props.permissionOptions.some(({ value }) => value === RESOURCE_PERMISSION.NOT_AUTH))

/* 查询与跨页选择 */
const { auth } = useStore()
const searchPermissionOptions = computed(() => RESOURCE_PERMISSION_OPTIONS.filter(({ value }) => !auth.isCE || value !== RESOURCE_PERMISSION.ROLE))
const searchFields = computed(() => [
  { label: '姓名', value: 'nick_name' },
  { label: '用户名', value: 'username' },
  { label: '权限', value: 'permission', multiple: true, options: searchPermissionOptions.value },
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
    .getResourceAuthorization(props.workspaceId, props.targetId, props.type, paginationConfig.value, searchQuery.value)
    .then(({ records, total }) => {
      permissionUsers.value = records.map((subject) => ({
        ...subject,
        permission: !canSelectNotAuth.value && subject.permission === RESOURCE_PERMISSION.NOT_AUTH ? RESOURCE_PERMISSION.VIEW : subject.permission,
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

/* 将单项与批量权限配置交给抽屉统一处理。 */
function handleOpenBatchConfig() {
  if (!selectedUsers.value.length || props.submitting) return
  emit(
    'configure',
    selectedUsers.value.map(({ id }) => id),
  )
}

function handlePermissionChange(value: string | number | boolean | undefined, subject: ResourceUserPermission) {
  const permission = props.permissionOptions.find((option) => option.value === value)?.value
  if (!permission || permission === subject.permission || props.submitting) return
  emit('configure', [subject.id], permission)
}

function refresh() {
  clearSelection()
  return loadPermissions()
}

defineExpose({ refresh })

/* 挂载当前标签时查询权限。 */
onMounted(() => loadPermissions())
</script>

<template>
  <div>
    <div class="flex-between mb-4 gap-4">
      <!-- 批量配置权限 -->
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
            <el-radio v-for="option in permissionOptions" :key="option.value" :value="option.value" class="mr-4!">{{ option.label }}</el-radio>
          </el-radio-group>
        </template>
      </el-table-column>
    </MkTable>
  </div>
</template>
