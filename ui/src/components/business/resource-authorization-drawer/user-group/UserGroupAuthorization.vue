<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import type ResourceAuthorizationApi from '@/api/admin/workspace/resource-authorization'
import { RESOURCE_PERMISSION } from '@/api/enums'
import type { Dict, ResourceAuthorizationTargetType, ResourcePermission, ResourceUserGroupPermission } from '@/api/types'
import MkTable from '@/components/global/mk-table/index.vue'
import UserGroupMembersDrawer from './UserGroupMembersDrawer.vue'

import type { ResourcePermissionOption } from '../types'

const props = defineProps<{
  api: typeof ResourceAuthorizationApi
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
const searchFields = [{ label: '名称', value: 'name' }]
const loading = ref(false)
const permissionGroups = ref<ResourceUserGroupPermission[]>([])
const selectedGroups = ref<ResourceUserGroupPermission[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 10, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const tableRef = useTemplateRef('tableRef')

function loadPermissions() {
  if (!props.targetId) return Promise.resolve()
  loading.value = true
  return props.api
    .getResourceUserGroupAuthorization(props.workspaceId, props.targetId, props.type, paginationConfig.value, searchQuery.value)
    .then(({ records, total }) => {
      permissionGroups.value = records.map((subject) => ({
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
  selectedGroups.value = []
  tableRef.value?.clearSelection()
}

function handleSearch(query?: Dict<unknown>) {
  searchQuery.value = query
  paginationConfig.value.currentPage = 1
  clearSelection()
  loadPermissions()
}

/* 查看用户组成员 */
const membersDrawerRef = useTemplateRef<InstanceType<typeof UserGroupMembersDrawer>>('membersDrawerRef')

function handleOpenMembersDrawer(group: ResourceUserGroupPermission) {
  const workspaceId = props.workspaceId
  if (!workspaceId) return
  membersDrawerRef.value?.open({ ...group, workspace_id: workspaceId })
}

function handleSelectionChange(selection: unknown[]) {
  selectedGroups.value = selection as ResourceUserGroupPermission[]
}

/* 将单项与批量权限配置交给抽屉统一处理。 */
function handleOpenBatchConfig() {
  if (!selectedGroups.value.length || props.submitting) return
  emit(
    'configure',
    selectedGroups.value.map(({ id }) => id),
  )
}

function handlePermissionChange(value: string | number | boolean | undefined, subject: ResourceUserGroupPermission) {
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
      <el-button type="primary" :disabled="!selectedGroups.length || loading || submitting" @click="handleOpenBatchConfig">配置权限</el-button>
      <MkComplexSearch :fields="searchFields" @change="handleSearch" />
    </div>
    <MkTable
      ref="tableRef"
      v-loading="loading || submitting"
      v-model:pagination-config="paginationConfig"
      :data="permissionGroups"
      :max-table-height="260"
      @current-change="loadPermissions"
      @size-change="loadPermissions"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="40" reserve-selection />
      <el-table-column prop="name" label="用户组" min-width="160" show-overflow-tooltip />
      <el-table-column label="成员数" min-width="100">
        <template #default="{ row }">
          <el-link type="primary" @click="handleOpenMembersDrawer(row)">{{ row.count }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="操作权限" min-width="340">
        <template #default="{ row }">
          <el-radio-group :model-value="row.permission" :disabled="submitting" @change="handlePermissionChange($event, row)">
            <el-radio v-for="option in permissionOptions" :key="option.value" :value="option.value" class="mr-4!">{{ option.label }}</el-radio>
          </el-radio-group>
        </template>
      </el-table-column>
    </MkTable>
    <UserGroupMembersDrawer ref="membersDrawerRef" />
  </div>
</template>
