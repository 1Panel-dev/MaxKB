<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, onMounted, reactive } from 'vue'

import { MsgConfirm, MsgError, MsgSuccess, MsgWarning } from '@/utils/message'
const props = defineProps<{ modelValue: DynamicFormValue }>()
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
    attrs: { multiple: formValue.value.multiple, data: formValue.value.treeData, filterable: true },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
  }
}
const render = (formData: DynamicFormValue) => {
  const attrs = formData.attrs || {}
  formValue.value.multiple = attrs.multiple
  formValue.value.treeData = attrs.data || []
  formValue.value.default_value = formData.default_value
  formValue.value.show_default_value = formData.show_default_value
}

defineExpose({ getData, render })
onMounted(() => {
  formValue.value.treeData = []
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

const treeProps = { children: 'children', label: 'label' }

const addDialog = reactive<{ visible: boolean; mode: AddMode; parentNode: TreeNode | null; formList: AddFormItem[] }>({
  visible: false,
  mode: 'root',
  parentNode: null,
  formList: [],
})

const editDialog = reactive<{ visible: boolean; targetNode: TreeNode | null; form: { label: string; value: string } }>({
  visible: false,
  targetNode: null,
  form: { label: '', value: '' },
})

function createId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function createEmptyRow(): AddFormItem {
  return { key: createId(), label: '', value: '' }
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

function closeAddDialog() {
  addDialog.visible = false
  addDialog.mode = 'root'
  addDialog.parentNode = null
  addDialog.formList = []
}

function submitAdd() {
  const validList = addDialog.formList
    .map((item) => ({ label: item.label.trim(), value: item.value.trim() }))
    .filter((item) => item.label && item.value)

  if (!validList.length) {
    MsgWarning('请至少填写一条完整数据')
    return
  }

  const newNodes: TreeNode[] = validList.map((item) => ({ id: createId(), label: item.label, value: item.value }))

  if (addDialog.mode === 'root') {
    formValue.value.treeData.push(...newNodes)
  } else {
    const parent = addDialog.parentNode
    if (!parent) {
      MsgError('未找到父节点')
      return
    }

    if (!parent.children) {
      parent.children = []
    }
    parent.children.push(...newNodes)
  }

  MsgSuccess('保存成功')
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
    MsgWarning('标签和选项值不能为空')
    return
  }

  if (!editDialog.targetNode) {
    MsgError('未找到父节点')
    return
  }

  editDialog.targetNode.label = label
  editDialog.targetNode.value = value

  MsgSuccess('保存成功')
  closeEditDialog()
}

/* -------------------- 删除 -------------------- */

function handleDelete(node: TreeNode) {
  MsgConfirm('提示', `确定删除「${node.label}」吗？`, { type: 'warning' })
    .then(() => {
      const removed = removeNodeById(formValue.value.treeData, node.id)
      if (removed) {
        MsgSuccess('删除成功')
      } else {
        MsgError('删除失败')
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

<template>
  <el-form-item prop="treeData" class="mk-hide-asterisk" :rules="[{ required: true, message: '请添加选项', blur: 'change', type: 'array', min: 1 }]">
    <template #label>
      <div class="flex-between">
        <span class="mk-required">选项</span>
        <div class="flex gap-3">
          <el-checkbox v-model="formValue.multiple" label="允许多选" />
          <el-button link type="primary" @click="openAddRootDialog">
            <MkIcon name="icon_add_outlined"></MkIcon>
          </el-button>
        </div>
      </div>
    </template>
    <el-card shadow="never" class="w-full" style="--el-card-padding: 12px">
      <el-tree :data="formValue.treeData" node-key="id" default-expand-all :expand-on-click-node="false" :props="treeProps" class="option-tree">
        <template #default="{ data, node }">
          <div class="flex-between min-w-0 flex-1 gap-2">
            <div class="min-w-0 flex-1 truncate" :title="`${data.label}-${data.value}`">{{ data.label }}-{{ data.value }}</div>
            <div class="flex shrink-0 items-center">
              <el-button text @click.stop="openEditDialog(data)">
                <MkIcon name="icon_edit_outlined"></MkIcon>
              </el-button>
              <el-button text @click.stop="openAddChildDialog(data)" v-if="node.level < 5">
                <MkIcon name="icon_add_outlined"></MkIcon>
              </el-button>

              <el-button text @click.stop="handleDelete(data)">
                <MkIcon name="icon_delete-trash_outlined"></MkIcon>
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>
  </el-form-item>

  <el-form-item
    class="mk-hide-asterisk"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: '请输入默认值' }] : []"
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">默认值</span>
        <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
      </div>
    </template>
    <el-tree-select
      v-model="formValue.default_value"
      :data="formValue.treeData"
      :multiple="formValue.multiple"
      :render-after-expand="false"
      style="width: 100%"
    />
  </el-form-item>
  <!-- 添加弹窗 -->
  <MkDialog v-model="addDialog.visible" :title="addDialog.mode === 'root' ? '添加一级选项' : '添加子选项'">
    <el-form :model="addDialog" label-position="top" require-asterisk-position="right" @submit.prevent>
      <MkFormList v-model="addDialog.formList" :default-item="createEmptyRow" item-key="key">
        <template #default="{ index, item: option }">
          <el-form-item :label="index === 0 ? '标签' : ''" :required="index === 0" class="min-w-0 flex-1 small">
            <el-input v-model.trim="option.label" placeholder="请输入选项标签" maxlength="50" />
          </el-form-item>
          <el-form-item :label="index === 0 ? '选项值' : ''" :required="index === 0" class="min-w-0 flex-1 small">
            <el-input v-model.trim="option.value" placeholder="请输入选项值" maxlength="100" />
          </el-form-item>
        </template>
      </MkFormList>
    </el-form>
    <template #footer>
      <el-button plain @click="closeAddDialog">取消</el-button>
      <el-button type="primary" @click="submitAdd">添加</el-button>
    </template>
  </MkDialog>

  <!-- 编辑弹窗 -->
  <MkDialog :close-on-click-modal="true" :close-on-press-escape="true" v-model="editDialog.visible" title="编辑">
    <el-form :model="editDialog.form" label-position="top" require-asterisk-position="right" @submit.prevent>
      <div class="flex gap-2">
        <el-form-item label="标签" required class="min-w-0 flex-1 small">
          <el-input v-model.trim="editDialog.form.label" placeholder="请输入选项标签" maxlength="50" />
        </el-form-item>
        <el-form-item label="选项值" required class="min-w-0 flex-1 small">
          <el-input v-model.trim="editDialog.form.value" placeholder="请输入选项值" maxlength="100" />
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <el-button plain @click="closeEditDialog">取消</el-button>
      <el-button type="primary" @click="submitEdit">保存</el-button>
    </template>
  </MkDialog>
</template>
