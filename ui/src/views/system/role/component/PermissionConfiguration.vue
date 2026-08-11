<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <el-scrollbar v-loading="loading" class="flex-1">
      <el-table
        :data="tableData"
        border
        size="small"
        style="width:100%"
        max-height="calc(100vh - 380px)"
        :span-method="mergeModuleCells"
      >
        <el-table-column prop="module" label="模块" min-width="140" />
        <el-table-column prop="name" label="操作对象" min-width="120" />
        <el-table-column label="权限类型" min-width="550">
          <template #header>
            <div class="flex items-center gap-3">
              <el-checkbox
                :model-value="allChecked"
                :indeterminate="allIndeterminate"
                :disabled="disabled"
                @change="toggleAll"
              >全选</el-checkbox>
            </div>
          </template>
          <template #default="{ row }">
            <div class="flex items-center flex-wrap gap-x-4 gap-y-1">
              <el-checkbox
                v-for="item in row.permission"
                :key="item.id"
                v-model="item.enable"
                :disabled="disabled"
              >
                <span class="text-sm whitespace-nowrap">{{ item.name }}</span>
              </el-checkbox>
              <el-button
                v-if="row.permission?.length"
                text
                type="primary"
                size="small"
                :disabled="disabled"
                @click="toggleRow(row)"
                class="ml-2"
              >{{ rowAllChecked(row) ? '取消全选' : '全选' }}</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-scrollbar>
    <div class="flex justify-end pt-4 border-t mt-4 shrink-0">
      <el-button type="primary" :disabled="disabled" :loading="saving" @click="handleSave">保存</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import roleApi from '@/api/system/role'
import type { RoleItem } from '@/api/type/role'

const props = defineProps<{ currentRole?: RoleItem }>()

const loading = ref(false)
const saving = ref(false)
const tableData = ref<any[]>([])
const disabled = computed(() => props.currentRole?.internal)

/** Merge consecutive cells with the same module name */
function mergeModuleCells({ row, _column, rowIndex, columnIndex }: any) {
  if (columnIndex === 0) {
    const same = tableData.value.filter((r) => r.module === row.module)
    const firstIdx = tableData.value.findIndex((r) => r.module === row.module)
    if (rowIndex === firstIdx) return { rowspan: same.length, colspan: 1 }
    return { rowspan: 0, colspan: 0 }
  }
}

function rowAllChecked(row: any): boolean {
  return row.permission?.length > 0 && row.permission.every((p: any) => p.enable)
}

function toggleRow(row: any) {
  const checked = !rowAllChecked(row)
  row.permission?.forEach((p: any) => (p.enable = checked))
}

const allChecked = computed(() => {
  const all = tableData.value.flatMap((r) => r.permission || [])
  return all.length > 0 && all.every((p: any) => p.enable)
})

const allIndeterminate = computed(() => {
  const all = tableData.value.flatMap((r) => r.permission || [])
  const someChecked = all.some((p: any) => p.enable)
  return someChecked && !all.every((p: any) => p.enable)
})

function toggleAll(checked: boolean) {
  tableData.value.forEach((row) => {
    row.permission?.forEach((p: any) => (p.enable = checked))
  })
}

async function getRolePermission() {
  if (!props.currentRole?.id) return
  loading.value = true
  try {
    const res = await roleApi.getRolePermissionList(props.currentRole.id, loading)
    tableData.value = []
    const data = res.data || []
    data.forEach((module: any) => {
      (module.children || []).forEach((feature: any) => {
        tableData.value.push({
          module: module.name,
          name: feature.name,
          permission: feature.permission,
        })
      })
    })
  } catch { tableData.value = [] }
}

async function handleSave() {
  saving.value = true
  try {
    const permissions = tableData.value.flatMap((row: any) =>
      (row.permission || []).map((p: any) => ({ id: p.id, enable: p.enable }))
    )
    await roleApi.saveRolePermission(props.currentRole?.id as string, permissions)
    ElMessage.success('保存成功')
  } catch (e) {
    console.error('[role] save permission failed:', e)
  }
  saving.value = false
}

watch(() => props.currentRole?.id, getRolePermission, { immediate: true })
</script>
