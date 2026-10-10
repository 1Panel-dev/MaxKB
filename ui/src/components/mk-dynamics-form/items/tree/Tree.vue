<script setup lang="ts">
import { computed, inject, nextTick, ref, toRaw, useAttrs, useTemplateRef, watch } from 'vue'
import { cloneDeep, isEqual } from 'lodash'
import { formItemContextKey, type TableInstance, type TreeNode } from 'element-plus'
import type { Dict } from '@/api/types'
import { post } from '@/api/admin/core/request'
import { getFileIconUrl } from '@/utils/icon'
import type { DynamicFormValue, FormField } from '../../type'

defineOptions({ name: 'DynamicFormTree', inheritAttrs: false })

interface DocumentRow extends Dict<DynamicFormValue> {
  hasChildren: boolean
}

const props = withDefaults(defineProps<{ modelValue?: DynamicFormValue; formField: FormField; otherParams: DynamicFormValue }>(), {
  modelValue: () => [],
})
const emit = defineEmits<{ 'update:modelValue': [value: DynamicFormValue[]]; change: [value: DynamicFormValue[]] }>()
const attrs = useAttrs()
const getExtra = inject<() => Dict<DynamicFormValue>>('get_extra')
const elFormItem = inject(formItemContextKey, undefined)

// 字段映射与表格数据，保留完整节点对象作为选中值。
const textField = computed(() => props.formField.text_field || 'label')
const valueField = computed(() => props.formField.value_field || 'value')
const childrenField = computed(() => props.formField.childrenField || 'children')
const options = computed(() => props.formField.option_list ?? [])
const lazy = computed(() => Boolean(props.formField.attrs?.lazy ?? attrs.lazy))
const documentRows = ref<DocumentRow[]>([])
const documentTableRef = useTemplateRef<{ tableRef?: TableInstance }>('documentTableRef')
const tableKey = ref(0)
const pendingLoads = ref(0)
const documentNodes = new Map<string | number, DocumentRow>()
const originalNodes = new WeakMap<DocumentRow, Dict<DynamicFormValue>>()
let restoringSelection = false

function normalizeDocuments(documents: Dict<DynamicFormValue>[]): DocumentRow[] {
  return documents.map((document) => {
    const row: DocumentRow = {
      ...document,
      hasChildren: lazy.value && (document.leaf === false || (document.leaf !== true && (document.type === 'folder' || !document.type))),
    }
    originalNodes.set(row, document)
    documentNodes.set(row[valueField.value], row)
    if (Array.isArray(document[childrenField.value])) {
      row[childrenField.value] = normalizeDocuments(document[childrenField.value])
    }
    return row
  })
}

function handleSelectionChange(selection: unknown[]) {
  if (restoringSelection) return
  const selectedDocuments = cloneDeep((selection as DocumentRow[]).map((row) => originalNodes.get(toRaw(row)) ?? row))
  if (isEqual(selectedDocuments, props.modelValue ?? [])) return
  emit('update:modelValue', selectedDocuments)
  emit('change', selectedDocuments)
  nextTick(() => elFormItem?.validate('change').catch(() => {}))
}

function restoreSelection() {
  const table = documentTableRef.value?.tableRef
  if (!table) return
  const selectedKeys = new Set((props.modelValue ?? []).map((document: Dict<DynamicFormValue>) => document[valueField.value]))
  restoringSelection = true
  table.clearSelection()
  documentNodes.forEach((row, key) => {
    if (row.is_exist || selectedKeys.has(key)) table.toggleRowSelection(row, true, true)
  })
  restoringSelection = false
  handleSelectionChange(table.getSelectionRows() as DocumentRow[])
}

// 懒加载沿用工具数据源协议，根目录不传 current_node。
function renderTemplate(template: string, data: Dict<DynamicFormValue>) {
  return template.replace(/\$\{(\w+)\}/g, (match, key) => (data[key] !== undefined ? String(data[key]) : match))
}
const requestUrl = computed(() =>
  renderTemplate(
    '/workspace/${current_workspace_id}/knowledge/${current_knowledge_id}/datasource/tool/${current_tool_id}/' +
      (props.formField.attrs?.fetch_list_function ?? attrs.fetch_list_function),
    { ...props.otherParams, ...getExtra?.() },
  ),
)

function loadDocuments(currentNode?: Dict<DynamicFormValue>) {
  pendingLoads.value += 1
  return post<{ current_node?: Dict<DynamicFormValue> }, Dict<DynamicFormValue>[]>(requestUrl.value, { current_node: currentNode })
    .then(normalizeDocuments)
    .finally(() => {
      pendingLoads.value -= 1
    })
}

function loadNode(document: DocumentRow, treeNode: TreeNode, resolve: (documents: DocumentRow[]) => void) {
  return loadDocuments(originalNodes.get(toRaw(document)) ?? document)
    .then((documents) => {
      resolve(documents)
      return nextTick(restoreSelection)
    })
    .catch(() => {
      // Table 无 reject 回调，恢复加载标记以便再次展开重试。
      treeNode.loading = false
    })
}

watch(
  [options, lazy, requestUrl],
  () => {
    documentNodes.clear()
    documentRows.value = []
    tableKey.value += 1
    if (!lazy.value) {
      documentRows.value = normalizeDocuments(options.value)
      return nextTick(restoreSelection)
    }
    return loadDocuments()
      .then((documents) => {
        documentRows.value = documents
        return nextTick(restoreSelection)
      })
      .catch(() => {
        // 请求层统一提示错误。
      })
  },
  { immediate: true, deep: true },
)
watch(() => props.modelValue, restoreSelection, { deep: true })
</script>

<template>
  <MkTable
    :key="tableKey"
    ref="documentTableRef"
    v-loading="pendingLoads > 0"
    :data="documentRows"
    :row-key="valueField"
    :tree-props="{ children: childrenField, hasChildren: 'hasChildren', checkStrictly: false }"
    :load="loadNode"
    :max-table-height="430"
    :lazy="lazy"
    @selection-change="handleSelectionChange"
  >
    <!-- 选择文档或文件夹，全选由表格维护 -->
    <el-table-column type="selection" width="40" reserve-selection :selectable="(row: DocumentRow) => !row.disabled && !row.is_exist" />
    <el-table-column class-name="expand-name-column" label="全部文档" :prop="textField">
      <template #default="{ row }: { row: DocumentRow }">
        <div class="flex-align-center min-w-0 flex-1 gap-2">
          <img v-if="row.icon" :src="row.icon" alt="" class="w-4.5 shrink-0" />
          <img v-else-if="row.type === 'folder'" src="@/assets/file-type/file-icon.svg" alt="" class="w-4.5 shrink-0" />
          <img
            v-else
            :src="
              getFileIconUrl(
                row.type === 'docx' ? `${row.name}.docx` : row.type === 'sheet' ? `${row.name}.xlsx` : String(row.name ?? row[textField] ?? ''),
              )
            "
            alt=""
            class="w-4.5 shrink-0"
          />
          <span :title="row[textField]" class="min-w-0 truncate">{{ row[textField] }}</span>
        </div>
      </template>
    </el-table-column>
  </MkTable>
</template>
