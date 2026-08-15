<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import RoleApi from '@/api/admin/system/role'
import type { RoleItem, RolePermission, RolePermissionModule } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

interface PermissionTableRow {
  id: string
  moduleId: string
  module: string
  name: string
  permissions: RolePermission[]
}

const props = defineProps<{ currentRole: RoleItem }>()

/* 权限数据加载与表格展示 */
const loading = ref(false)
const permissionData = ref<PermissionTableRow[]>([])
const disabled = computed(() => props.currentRole.internal)
const permissionTableKey = computed(
  () => `${props.currentRole.id}:${disabled.value ? 'readonly' : 'editable'}`,
)

function loadPermissions() {
  loading.value = true
  permissionData.value = []
  return RoleApi.getRolePermissionList(props.currentRole.id).then((permissions) => {
    permissionData.value = transformPermissions(permissions)
    loading.value = false
  })
}

function transformPermissions(modules: RolePermissionModule[]) {
  return modules.flatMap((module) =>
    module.children.map((feature) => ({
      id: `${module.id}:${feature.id}`,
      moduleId: module.id,
      module: module.name,
      name: feature.name,
      permissions: feature.permission,
    })),
  )
}

function permissionTableSpan({
  row,
  rowIndex,
  columnIndex,
}: {
  row: PermissionTableRow
  rowIndex: number
  columnIndex: number
}) {
  if (columnIndex !== 0) return [1, 1]
  const firstRowIndex = permissionData.value.findIndex(({ moduleId }) => moduleId === row.moduleId)
  return rowIndex === firstRowIndex
    ? [permissionData.value.filter(({ moduleId }) => moduleId === row.moduleId).length, 1]
    : [0, 0]
}

/* 单项权限与查看权限联动 */
function handlePermissionChange(
  value: boolean,
  permission: RolePermission,
  row: PermissionTableRow,
) {
  permission.enable = value
  if (row.permissions.some(({ id }) => id.includes('OTHER'))) return
  const readPermission = row.permissions.find(({ id }) => /:READ$/.test(id))
  if (value && permission.id !== readPermission?.id && readPermission) readPermission.enable = true
  if (!value && permission.id === readPermission?.id) {
    row.permissions.forEach((item) => (item.enable = false))
  }
}

/* 行选择与全表选择 */
function getPermissionState(permissions: RolePermission[]) {
  const checkedCount = permissions.filter(({ enable }) => enable).length
  return {
    checked: permissions.length > 0 && checkedCount === permissions.length,
    indeterminate: checkedCount > 0 && checkedCount < permissions.length,
  }
}

function handleRowChange(value: boolean, row: PermissionTableRow) {
  row.permissions.forEach((permission) => {
    permission.enable = value
  })
}

const allPermissions = computed(() =>
  permissionData.value.flatMap(({ permissions }) => permissions),
)
const allPermissionState = computed(() => getPermissionState(allPermissions.value))

function handleCheckAll(value: boolean) {
  permissionData.value.forEach((row) => handleRowChange(value, row))
}

/* 权限配置保存 */
function handleSave() {
  loading.value = true
  const permissions = permissionData.value.flatMap((row) =>
    row.permissions.map(({ id, enable }) => ({ id, enable })),
  )
  RoleApi.postRolePermissions(props.currentRole.id, permissions)
    .then(() => MsgSuccess('保存成功'))
    .finally(() => {
      loading.value = false
    })
}

watch(() => props.currentRole.id, loadPermissions, { immediate: true })
</script>

<template>
  <div class="relative flex min-h-0 flex-1 flex-col">
    <MkTable
      :key="permissionTableKey"
      class="role-permission-table"
      row-key="id"
      :span-method="permissionTableSpan"
      :max-table-height="disabled ? 200 : 240"
      :data="permissionData"
      v-loading="loading"
    >
      <el-table-column prop="module" label="模块名称" width="150" />
      <el-table-column prop="name" label="操作对象" width="150" />
      <el-table-column label="权限">
        <template #default="{ row }">
          <div class="flex-wrap">
            <template v-for="permission in row.permissions" :key="permission.id">
              <el-checkbox
                v-model="permission.enable"
                :disabled="disabled"
                class="w-30"
                @change="(value: boolean) => handlePermissionChange(value, permission, row)"
                >{{ permission.name }}</el-checkbox
              >
            </template>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        class-name="permission-checkbox-column"
        label-class-name="permission-checkbox-column"
        :width="60"
      >
        <template #header>
          <el-checkbox
            :model-value="allPermissionState.checked"
            :indeterminate="allPermissionState.indeterminate"
            :disabled="disabled"
            @change="handleCheckAll"
          />
        </template>

        <template #default="{ row }">
          <el-checkbox
            :model-value="getPermissionState(row.permissions).checked"
            :indeterminate="getPermissionState(row.permissions).indeterminate"
            :disabled="disabled"
            @change="(value: boolean) => handleRowChange(value, row)"
          />
        </template>
      </el-table-column>
    </MkTable>

    <footer
      v-if="!disabled"
      class="sticky -mb-6 -ml-6 -mr-6 bottom-0 z-10 mt-auto flex shrink-0 justify-end border-t bg-white px-6 py-4"
    >
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </footer>
  </div>
</template>

<style scoped lang="scss">
:deep(.role-permission-table.el-table) {
  border: 1px solid var(--el-table-border-color);

  .el-table__cell {
    border-bottom: 1px solid var(--el-table-border-color);
    border-right: 1px solid var(--el-table-border-color);

    &:last-child {
      border-right: 0;
    }
  }

  thead th.el-table__cell {
    border-bottom: 1px solid var(--el-table-border-color) !important;
  }

  .permission-checkbox-column .cell {
    align-items: center;
    display: flex;
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }
}
</style>
