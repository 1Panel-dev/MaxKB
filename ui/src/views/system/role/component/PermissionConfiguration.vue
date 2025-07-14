<template>
  <el-scrollbar v-loading="loading">
    <app-table :data="tableData" border :span-method="objectSpanMethod" :maxTableHeight="280">
      <el-table-column prop="module" :width="150" :label="$t('views.role.permission.moduleName')"/>
      <el-table-column
        prop="name"
        :width="150"
        :label="$t('views.role.permission.operationTarget')"
      />
      <el-table-column prop="permission" :label="$t('views.model.modelForm.permissionType.label')">
        <template #default="{ row }">
          <el-checkbox
            v-for="item in row.permission"
            :key="item.id"
            v-model="item.enable"
            :disabled="disabled"
            @change="(val: boolean) => handleCellChange(val, item, row)"
          >
            <div class="ellipsis" style="width: 96px">{{ item.name }}</div>
          </el-checkbox>
        </template>
      </el-table-column>
      <el-table-column :width="40">
        <template #header>
          <el-checkbox
            :model-value="allChecked"
            :indeterminate="allIndeterminate"
            :disabled="disabled"
            @change="handleCheckAll"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            v-model="row.enable"
            :indeterminate="row.indeterminate"
            :disabled="disabled"
            @change="(value: boolean) => handleRowChange(value, row)"
          />
        </template>
      </el-table-column>
    </app-table>
  </el-scrollbar>
  <div class="footer border-t">
    <el-button type="primary" :disabled="disabled" :loading="loading" @click="handleSave">
      {{ $t('common.save') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import {ref, watch, computed} from 'vue'
import type {
  RoleItem,
  RolePermissionItem,
  RoleTableDataItem,
  ChildrenPermissionItem,
} from '@/api/type/role'
import {loadPermissionApi} from '@/utils/dynamics-api/permission-api'
import RoleApi from '@/api/system/role'
import {MsgSuccess} from '@/utils/message'
import {t} from '@/locales'
import {hasPermission} from "@/utils/permission";
import {EditionConst, RoleConst} from "@/utils/permission/data.ts";
import { max } from 'moment'

const props = defineProps<{
  currentRole?: RoleItem
}>()

const loading = ref(false)
const tableData = ref<RoleTableDataItem[]>([])
const needDisable = computed(() => {
  const isEeOrPe = hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')
  const isAdminOrExtendAdmin = hasPermission([RoleConst.ADMIN, RoleConst.EXTENDS_ADMIN], 'OR')
  const isWorkspaceManage =
    hasPermission(
    [
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      RoleConst.EXTENDS_WORKSPACE_MANAGE.getWorkspaceRole,
    ],
      'OR'
  )

  if (!isEeOrPe) {
    return false
  }

  if (isAdminOrExtendAdmin) {
    return false
  }

  return isWorkspaceManage
})
const disabled = computed(() => props.currentRole?.internal || needDisable.value)

function transformData(data: RolePermissionItem[]) {
  const transformedData: RoleTableDataItem[] = []
  data.forEach((module) => {
    module.children.forEach((feature) => {
      const perChecked = feature.permission.filter((p) => p.enable).map((p) => p.id)

      transformedData.push({
        module: module.name,
        name: feature.name,
        permission: feature.permission,
        enable: feature.enable,
        perChecked,
        indeterminate: perChecked.length > 0 && perChecked.length < feature.permission.length,
      })
    })
  })
  return transformedData
}

async function getRolePermission() {
  if (!props.currentRole?.id) return
  try {
    tableData.value = []
    const res = await RoleApi.getRolePermissionList(props.currentRole.id, loading)
    tableData.value = transformData(res.data)
  } catch (error) {
    console.error(error)
  }
}

function handleCellChange(
  value: boolean,
  item: ChildrenPermissionItem,
  row: RoleTableDataItem,
) {
  item.enable = value
  const readItem = row.permission.find((p) => /:READ$/.test(p.id))
  // 如果勾选的不是 READ，则强制把 READ 也勾上
  if (value && item.id !== readItem?.id && readItem && !readItem.enable) {
    readItem.enable = true
  } else if (!value && item.id === readItem?.id) {
    // 取消 READ 整行其他权限全部取消
    row.permission.forEach((p) => (p.enable = false))
  }

  const checkedIds = row.permission.filter((p) => p.enable).map((p) => p.id)
  row.perChecked = checkedIds
  row.enable = checkedIds.length === row.permission.length
  row.indeterminate =
    checkedIds.length > 0 && checkedIds.length < row.permission.length
}

function handleRowChange(checked: boolean, row: RoleTableDataItem) {
  if (checked) {
    row.permission.forEach((p) => (p.enable = true))
  } else {
    row.permission.forEach((p) => (p.enable = false))
  }
  row.perChecked = checked ? row.permission.map((p) => p.id) : []
  row.indeterminate = false
}

const allChecked = computed(() => {
  return tableData.value.length > 0 && tableData.value.every((item) => item.enable)
})

const allIndeterminate = computed(() => {
  return !allChecked.value && tableData.value.some((item) => item.enable)
})

function handleCheckAll(checked: boolean) {
  tableData.value.forEach((item) => {
    item.enable = checked
    item.perChecked = checked ? item.permission.map((p) => p.id) : []
    item.indeterminate = false
    item.permission.forEach((p) => (p.enable = checked))
  })
}

const objectSpanMethod = ({row, column, rowIndex, columnIndex}: any) => {
  if (columnIndex === 0) {
    const sameModuleRows = tableData.value.filter((item) => item.module === row.module)
    const firstRowIndex = tableData.value.findIndex((item) => item.module === row.module)
    if (rowIndex === firstRowIndex) {
      return {
        rowspan: sameModuleRows.length,
        colspan: 1,
      }
    } else {
      return {
        rowspan: 0,
        colspan: 0,
      }
    }
  }
}

watch(() => props.currentRole?.id, getRolePermission, {immediate: true})

async function handleSave() {
  try {
    const permissions = tableData.value.flatMap((row) =>
      row.permission.map((p) => ({ id: p.id, enable: p.enable })),
    )
    await loadPermissionApi('role').saveRolePermission(props.currentRole?.id as string, permissions, loading)
    MsgSuccess(t('common.saveSuccess'))
  } catch (error) {
    console.log(error)
  }
}
</script>

<style lang="scss" scoped>
:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  box-sizing: border-box;
}
</style>
