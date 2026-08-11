<template>
  <div class="flex-1 flex flex-col p-4 overflow-hidden">
    <h4 class="text-sm font-semibold mb-3 shrink-0" style="color:var(--mk-N900)">权限设置</h4>

    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-3 shrink-0 flex-wrap gap-2">
      <el-button size="small" :disabled="multipleSelection.length === 0" @click="openBatchDialog">
        批量配置
      </el-button>
      <div class="flex items-center gap-2">
        <el-select v-model="searchType" size="small" style="width:80px" @change="onSearchTypeChange">
          <el-option label="名称" value="name" />
          <el-option label="权限" value="permission" />
        </el-select>
        <el-input
          v-if="searchType === 'name'"
          v-model="searchName"
          placeholder="搜索"
          clearable
          size="small"
          style="width:200px"
        />
        <el-select
          v-else
          v-model="searchPermissions"
          placeholder="选择权限"
          clearable
          multiple
          collapse-tags
          collapse-tags-tooltip
          size="small"
          style="width:200px"
        >
          <el-option label="不授权" value="NOT_AUTH" />
          <el-option label="查看" value="VIEW" />
          <el-option label="管理" value="MANAGE" />
        </el-select>
      </div>
    </div>

    <!-- Permission table (tree mode) -->
    <el-table
      ref="tableRef"
      :data="filteredData"
      border
      stripe
      size="small"
      style="width:100%"
      row-key="id"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      :default-expand-all="true"
      :max-height="'calc(100vh - 320px)'"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="44" :reserve-selection="true" />
      <el-table-column prop="name" label="名称" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="flex items-center gap-2">
            <MkIcon
              v-if="row.resource_type === 'folder'"
              name="icon_folder_outlined"
              :size="16"
            />
            <MkIcon
              v-else
              name="icon_document_outlined"
              :size="16"
            />
            {{ row.name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="权限类型" min-width="240">
        <template #default="{ row }">
          <el-radio-group
            :model-value="row.permission || 'NOT_AUTH'"
            size="small"
            @change="(val: any) => onPermissionChange(val, row)"
          >
            <el-radio-button
              v-for="opt in getRowOptions(row)"
              :key="opt.value"
              :value="opt.value"
            >{{ opt.label }}</el-radio-button>
          </el-radio-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- Batch dialog -->
    <el-dialog v-model="batchVisible" title="批量配置权限" width="420" destroy-on-close>
      <el-radio-group v-model="batchValue" class="flex flex-col gap-4">
        <el-radio value="NOT_AUTH">
          <div class="text-sm">不授权</div>
          <div class="text-xs text-gray-400">取消对此资源的授权</div>
        </el-radio>
        <el-radio value="VIEW">
          <div class="text-sm">查看</div>
          <div class="text-xs text-gray-400">仅可查看资源内容</div>
        </el-radio>
        <el-radio value="MANAGE">
          <div class="text-sm">管理</div>
          <div class="text-xs text-gray-400">可查看、编辑及删除资源</div>
        </el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="batchVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!batchValue" @click="submitBatch">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  data: any[]
  type: string
}>()

const emit = defineEmits<{
  submitPermissions: [payload: any[]]
}>()

// ---- search ----
const searchType = ref('name')
const searchName = ref('')
const searchPermissions = ref<string[]>([])

function onSearchTypeChange() {
  searchName.value = ''
  searchPermissions.value = []
}

function matchNode(node: any, name: string, permissions: string[]): boolean {
  let ok = true
  if (name) ok = ok && node.name?.toLowerCase().includes(name.toLowerCase())
  if (permissions.length) ok = ok && permissions.includes(node.permission || 'NOT_AUTH')
  return ok
}

function filterTree(nodes: any[], name: string, permissions: string[]): any[] {
  if (!nodes?.length) return []
  if (!name && !permissions.length) return nodes
  const out: any[] = []
  for (const n of nodes) {
    const clone = { ...n }
    const kids = n.children ? filterTree(n.children, name, permissions) : []
    if (matchNode(n, name, permissions) || kids.length) {
      clone.children = kids
      out.push(clone)
    }
  }
  return out
}

const filteredData = computed(() => {
  return filterTree(props.data, searchName.value, searchPermissions.value)
})

// ---- permission options ----
function getRowOptions(row: any) {
  const isFolder = row.resource_type === 'folder'
  const isRoot = isFolder && !row.folder_id
  if (isRoot) {
    return [
      { label: '查看', value: 'VIEW' },
      { label: '管理', value: 'MANAGE' },
    ]
  }
  return [
    { label: '不授权', value: 'NOT_AUTH' },
    { label: '查看', value: 'VIEW' },
    { label: '管理', value: 'MANAGE' },
  ]
}

// ---- multi-select ----
const tableRef = ref()
const multipleSelection = ref<any[]>([])

function onSelectionChange(selection: any[]) {
  multipleSelection.value = selection
}

// ---- batch dialog ----
const batchVisible = ref(false)
const batchValue = ref('')

function openBatchDialog() {
  batchValue.value = ''
  batchVisible.value = true
}

function submitBatch() {
  if (!batchValue.value || !multipleSelection.value.length) return
  const payload = multipleSelection.value.map((r) => ({
    target_id: r.id,
    permission: batchValue.value,
  }))
  emit('submitPermissions', payload)
  batchVisible.value = false
  tableRef.value?.clearSelection()
}

// ---- single change with inheritance ----
function collectDescendantIds(nodes: any[]): string[] {
  if (!nodes) return []
  const ids: string[] = []
  for (const n of nodes) {
    ids.push(n.id)
    if (n.children) ids.push(...collectDescendantIds(n.children))
  }
  return ids
}

function onPermissionChange(value: string, row: any) {
  const payload: any[] = [{ target_id: row.id, permission: value }]

  // Folder -> VIEW/MANAGE: propagate NOT_AUTH children to VIEW
  if (row.resource_type === 'folder' && ['VIEW', 'MANAGE'].includes(value)) {
    const walk = (nodes: any[]) => {
      for (const n of nodes || []) {
        if (n.permission === 'NOT_AUTH' || n.permission == null) {
          payload.push({ target_id: n.id, permission: 'VIEW' })
        }
        if (n.children) walk(n.children)
      }
    }
    walk(row.children)
  }

  // Folder -> NOT_AUTH: all descendants also NOT_AUTH
  if (row.resource_type === 'folder' && value === 'NOT_AUTH') {
    for (const id of collectDescendantIds(row.children)) {
      payload.push({ target_id: id, permission: 'NOT_AUTH' })
    }
  }

  row.permission = value
  emit('submitPermissions', payload)
}
</script>
