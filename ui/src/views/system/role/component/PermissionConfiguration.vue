<template>
  <el-scrollbar v-loading="loading">
    <div class="p-24 pt-0">
      <el-table :data="tableData" border :span-method="objectSpanMethod">
        <el-table-column prop="module" :width="130" :label="$t('views.role.permission.moduleName')" />
        <el-table-column prop="name" :width="150" :label="$t('views.role.permission.operationTarget')" />
        <el-table-column prop="permission" :label="$t('views.model.modelForm.permissionType.label')">
          <template #default="{ row }">
            <el-checkbox-group v-model="row.perChecked" @change="handleCellChange($event, row)">
              <el-checkbox v-for="item in row.permission" :key="item.id" :value="item.id" :disabled="disabled">
                <div class="ellipsis" style="width: 96px">{{ item.name }}</div>
              </el-checkbox>
            </el-checkbox-group>
          </template>
        </el-table-column>
        <el-table-column :width="40">
          <template #header>
            <el-checkbox :model-value="allChecked" :indeterminate="allIndeterminate" :disabled="disabled"
              @change="handleCheckAll" />
          </template>
          <template #default="{ row }">
            <el-checkbox v-model="row.enable" :indeterminate="row.indeterminate" :disabled="disabled"
              @change="(value: boolean) => handleRowChange(value, row)" />
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-scrollbar>
  <div v-if="!disabled" class="footer border-t">
    <el-button type="primary" style="width: 80px;" :loading="loading" @click="handleSave">
      {{ $t('common.save') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { RoleItem, RolePermissionItem, RoleTableDataItem, ChildrenPermissionItem } from '@/api/type/role'
import RoleApi from '@/api/system/role'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'

const props = defineProps<{
  currentRole?: RoleItem
}>()

const loading = ref(false)
const tableData = ref<RoleTableDataItem[]>([])
const disabled = computed(() => props.currentRole?.internal) // TODO 权限

function transformData(data: RolePermissionItem[]) {
  const transformedData: RoleTableDataItem[] = []
  data.forEach(module => {
    module.children.forEach(feature => {
      const perChecked = feature.permission
        .filter(p => p.enable)
        .map(p => p.id)

      transformedData.push({
        module: module.name,
        name: feature.name,
        permission: feature.permission,
        enable: feature.enable,
        perChecked,
        indeterminate: perChecked.length > 0 && perChecked.length < feature.permission.length
      })
    })
  })
  return transformedData;
};

async function getRolePermission() {
  if (!props.currentRole?.id) return
  try {
    tableData.value = [];
    const res = await RoleApi.getRolePermissionList(props.currentRole.id, loading)
    tableData.value = transformData(res.data);
  } catch (error) {
    console.error(error)
  }
}

function handleCellChange(checkedValues: string[], row: RoleTableDataItem) {
  row.enable = checkedValues.length === row.permission.length
  row.indeterminate = checkedValues.length > 0 && checkedValues.length < row.permission.length

  row.permission.forEach(p => {
    p.enable = checkedValues.includes(p.id)
  })
}

function handleRowChange(checked: boolean, row: RoleTableDataItem) {
  if (checked) {
    row.perChecked = row.permission.map(p => p.id)
    row.permission.forEach(p => p.enable = true)
  } else {
    row.perChecked = []
    row.permission.forEach(p => p.enable = false)
  }
  row.indeterminate = false
}

const allChecked = computed(() => {
  return tableData.value.length > 0 && tableData.value.every(item => item.enable)
})

const allIndeterminate = computed(() => {
  return !allChecked.value && tableData.value.some(item => item.enable)
})

function handleCheckAll(checked: boolean) {
  tableData.value.forEach(item => {
    item.enable = checked
    item.perChecked = checked ? item.permission.map(p => p.id) : []
    item.indeterminate = false
    item.permission.forEach(p => p.enable = checked)
  })
}

const objectSpanMethod = ({ row, column, rowIndex, columnIndex }: any) => {
  if (columnIndex === 0) {
    const sameModuleRows = tableData.value.filter(item => item.module === row.module)
    const firstRowIndex = tableData.value.findIndex(item => item.module === row.module)
    if (rowIndex === firstRowIndex) {
      return {
        rowspan: sameModuleRows.length,
        colspan: 1
      }
    } else {
      return {
        rowspan: 0,
        colspan: 0
      }
    }
  }
}

watch(() => props.currentRole?.id, getRolePermission, { immediate: true })

async function handleSave() {
  try {
    const permissions: { id: string, enable: boolean }[] = [];
    tableData.value.forEach((e) => {
      e.permission?.forEach((ele: ChildrenPermissionItem) => {
        permissions.push({
          id: ele.id,
          enable: ele.enable,
        });
      });
    });
    await RoleApi.saveRolePermission(props.currentRole?.id as string, permissions, loading);
    MsgSuccess(t('common.saveSuccess'))
  } catch (error) {
    console.log(error);
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