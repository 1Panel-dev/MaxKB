<template>
  <el-form-item>
    <template #label>
      <div class="flex-between">
        <span>
          {{ $t('dynamicsForm.TreeSelect.select') }}
          <span class="color-danger">*</span>
        </span>
        <div class="flex">
          <el-checkbox v-model="formValue.multiple" label="允许多选" size="large" class="pr-8" />
          <el-button link type="primary" @click="openAddRootDialog">
            <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
            {{ $t('common.add') }}
          </el-button>
        </div>
      </div>
    </template>

    <el-tree
      :data="treeData"
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      :props="treeProps"
      class="option-tree"
    >
      <template #default="{ data }">
        <div class="tree-node">
          <div class="tree-node__main">
            <span class="tree-node__label">{{ data.label }}</span>
            <span class="tree-node__colon">：</span>
            <span class="tree-node__value">{{ data.value }}</span>
          </div>

          <div class="tree-node__actions">
            <el-button link type="primary" @click.stop="openAddChildDialog(data)">
              <el-icon class="action-btn">
                <Plus />
              </el-icon>
            </el-button>

            <el-button link type="primary" @click.stop="openEditDialog(data)">
              <el-icon class="action-btn"> <Edit /></el-icon>
            </el-button>

            <el-button link type="danger" @click.stop="handleDelete(data)">
              <el-icon class="action-btn"> <Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
    </el-tree>
  </el-form-item>

  <el-form-item
    class="defaultValueItem"
    :required="formValue.required"
    prop="default_value"
    :label="$t('dynamicsForm.default.label')"
    :rules="
      formValue.required
        ? [
            {
              required: true,
              message: `${$t('dynamicsForm.default.label')}${$t('dynamicsForm.default.requiredMessage')}`,
            },
          ]
        : []
    "
  >
    <el-tree-select
      v-model="formValue.default_value"
      :data="treeData"
      :multiple="formValue.multiple"
      :render-after-expand="false"
      style="width: 100%"
    />
  </el-form-item>
  <!-- 添加弹窗 -->
  <el-dialog
    v-model="addDialog.visible"
    :title="
      addDialog.mode === 'root'
        ? $t('dynamicsForm.TreeSelect.addDialog.addFirstOption')
        : $t('dynamicsForm.TreeSelect.addDialog.addSubOptions')
    "
    width="520px"
    destroy-on-close
  >
    <div class="dialog-body">
      <div v-for="(item, index) in addDialog.formList" :key="item.key" class="dialog-row">
        <el-input
          v-model.trim="item.label"
          :placeholder="$t('dynamicsForm.tag.placeholder')"
          maxlength="50"
        />
        <el-input
          v-model.trim="item.value"
          :placeholder="$t('dynamicsForm.Select.placeholder')"
          maxlength="100"
        />
        <el-button
          link
          type="danger"
          :disabled="addDialog.formList.length === 1"
          @click="removeAddRow(index)"
        >
          <el-icon class="action-btn"> <Delete /></el-icon>
        </el-button>
      </div>

      <el-button link type="primary" @click="appendAddRow">
        <AppIcon iconName="app-add-outlined" class="mr-4" />
        {{ $t('common.add') }}
      </el-button>
    </div>

    <template #footer>
      <el-button @click="closeAddDialog">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submitAdd">{{ $t('common.add') }}</el-button>
    </template>
  </el-dialog>

  <!-- 编辑弹窗 -->
  <el-dialog v-model="editDialog.visible" :title="$t('common.edit')" width="520px" destroy-on-close>
    <div class="dialog-body">
      <div class="dialog-row dialog-row--edit">
        <el-input
          v-model.trim="editDialog.form.label"
          :placeholder="$t('dynamicsForm.tag.placeholder')"
          maxlength="50"
        />
        <el-input
          v-model.trim="editDialog.form.value"
          :placeholder="$t('dynamicsForm.Select.placeholder')"
          maxlength="100"
        />
      </div>
    </div>

    <template #footer>
      <el-button @click="closeEditDialog">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submitEdit">{{ $t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, onMounted, watch, ref, reactive } from 'vue'
import { Edit, Plus, Delete } from '@element-plus/icons-vue'
import { t } from '@/locales/'

import { ElMessage, ElMessageBox } from 'element-plus'
const props = defineProps<{
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const getData = () => {
  return {
    input_type: 'TreeSelect',
    attrs: { multiple: formValue.value.multiple, data: treeData.value },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
  }
}
const rander = (form_data: any) => {
  const attrs = form_data.attrs || {}
  formValue.value.multiple = attrs.multiple
  treeData.value = attrs.data || []
  formValue.value.default_value = form_data.default_value
  formValue.value.show_default_value = form_data.show_default_value
}

defineExpose({ getData, rander })
onMounted(() => {
  formValue.value.default_value = ''
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})

interface TreeNode {
  id: string
  label: string
  value: string
  children?: TreeNode[]
}

interface AddFormItem {
  key: string
  label: string
  value: string
}

type AddMode = 'root' | 'child'

const treeProps = {
  children: 'children',
  label: 'label',
}

const treeData = ref<TreeNode[]>([])

const addDialog = reactive<{
  visible: boolean
  mode: AddMode
  parentNode: TreeNode | null
  formList: AddFormItem[]
}>({
  visible: false,
  mode: 'root',
  parentNode: null,
  formList: [],
})

const editDialog = reactive<{
  visible: boolean
  targetNode: TreeNode | null
  form: {
    label: string
    value: string
  }
}>({
  visible: false,
  targetNode: null,
  form: {
    label: '',
    value: '',
  },
})

function createId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function createEmptyRow(): AddFormItem {
  return {
    key: createId(),
    label: '',
    value: '',
  }
}

/* -------------------- 添加 -------------------- */

function openAddRootDialog() {
  addDialog.visible = true
  addDialog.mode = 'root'
  addDialog.parentNode = null
  addDialog.formList = [createEmptyRow()]
}

function openAddChildDialog(node: TreeNode) {
  addDialog.visible = true
  addDialog.mode = 'child'
  addDialog.parentNode = node
  addDialog.formList = [createEmptyRow()]
}

function appendAddRow() {
  addDialog.formList.push(createEmptyRow())
}

function removeAddRow(index: number) {
  if (addDialog.formList.length === 1) return
  addDialog.formList.splice(index, 1)
}

function closeAddDialog() {
  addDialog.visible = false
  addDialog.mode = 'root'
  addDialog.parentNode = null
  addDialog.formList = []
}

function submitAdd() {
  const validList = addDialog.formList
    .map((item) => ({
      label: item.label.trim(),
      value: item.value.trim(),
    }))
    .filter((item) => item.label && item.value)

  if (!validList.length) {
    ElMessage.warning(t('dynamicsForm.TreeSelect.addDialog.require'))
    return
  }

  const newNodes: TreeNode[] = validList.map((item) => ({
    id: createId(),
    label: item.label,
    value: item.value,
  }))

  if (addDialog.mode === 'root') {
    treeData.value.push(...newNodes)
  } else {
    const parent = addDialog.parentNode
    if (!parent) {
      ElMessage.error(t('dynamicsForm.TreeSelect.addDialog.nodeNotFound'))
      return
    }

    if (!parent.children) {
      parent.children = []
    }
    parent.children.push(...newNodes)
  }

  ElMessage.success(t('common.saveSuccess'))
  closeAddDialog()
}

/* -------------------- 编辑 -------------------- */

function openEditDialog(node: TreeNode) {
  editDialog.visible = true
  editDialog.targetNode = node
  editDialog.form.label = node.label
  editDialog.form.value = node.value
}

function closeEditDialog() {
  editDialog.visible = false
  editDialog.targetNode = null
  editDialog.form.label = ''
  editDialog.form.value = ''
}

function submitEdit() {
  const label = editDialog.form.label.trim()
  const value = editDialog.form.value.trim()

  if (!label || !value) {
    ElMessage.warning(t('dynamicsForm.TreeSelect.addDialog.tagRequire'))
    return
  }

  if (!editDialog.targetNode) {
    ElMessage.error(t('dynamicsForm.TreeSelect.addDialog.nodeNotFound'))
    return
  }

  editDialog.targetNode.label = label
  editDialog.targetNode.value = value

  ElMessage.success(t('common.saveSuccess'))
  closeEditDialog()
}

/* -------------------- 删除 -------------------- */

function handleDelete(node: TreeNode) {
  ElMessageBox.confirm(`${t('common.deleteConfirm')}「${node.label}」`, t('common.tip'), {
    type: 'warning',
  })
    .then(() => {
      const removed = removeNodeById(treeData.value, node.id)
      if (removed) {
        ElMessage.success(t('common.deleteSuccess'))
      } else {
        ElMessage.error(t('common.deleteError'))
      }
    })
    .catch(() => {})
}

function removeNodeById(list: TreeNode[], targetId: string): boolean {
  const index = list.findIndex((item) => item.id === targetId)
  if (index !== -1) {
    list.splice(index, 1)
    return true
  }

  for (const item of list) {
    if (item.children?.length) {
      const removed = removeNodeById(item.children, targetId)
      if (removed) {
        if (item.children.length === 0) {
          delete item.children
        }
        return true
      }
    }
  }

  return false
}
</script>
<style lang="scss" scoped>
.defaultValueItem {
  position: relative;
  .defaultValueCheckbox {
    position: absolute;
    right: 0;
    top: -35px;
  }
}
.dynamic-option-tree {
  width: 100%;
}

.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.tree-header__title {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.required {
  color: var(--el-color-danger);
}

.tree-empty {
  width: 100%;
  padding: 24px 0;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
}
.option-tree {
  width: 100%;
}
.option-tree :deep(.el-tree-node__content) {
  height: 18px;
}

.tree-node {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-right: 8px;
}

.tree-node__main {
  display: flex;
  align-items: center;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
}

.tree-node__label,
.tree-node__colon,
.tree-node__value {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.tree-node__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.tree-node:hover .tree-node__actions {
  opacity: 1;
}

.dialog-body {
  padding-top: 8px;
}

.dialog-row {
  display: grid;
  grid-template-columns: 1fr 1fr 40px;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.dialog-row--edit {
  grid-template-columns: 1fr 1fr;
}
</style>
