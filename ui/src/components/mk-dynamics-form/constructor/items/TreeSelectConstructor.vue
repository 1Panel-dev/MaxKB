<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, onMounted, reactive } from 'vue'

import { ElMessage, ElMessageBox } from 'element-plus'
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
  const validList = addDialog.formList.map((item) => ({ label: item.label.trim(), value: item.value.trim() })).filter((item) => item.label && item.value)

  if (!validList.length) {
    ElMessage.warning('请至少填写一条完整数据')
    return
  }

  const newNodes: TreeNode[] = validList.map((item) => ({ id: createId(), label: item.label, value: item.value }))

  if (addDialog.mode === 'root') {
    formValue.value.treeData.push(...newNodes)
  } else {
    const parent = addDialog.parentNode
    if (!parent) {
      ElMessage.error('未找到父节点')
      return
    }

    if (!parent.children) {
      parent.children = []
    }
    parent.children.push(...newNodes)
  }

  ElMessage.success('保存成功')
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
    ElMessage.warning('标签和选项值不能为空')
    return
  }

  if (!editDialog.targetNode) {
    ElMessage.error('未找到父节点')
    return
  }

  editDialog.targetNode.label = label
  editDialog.targetNode.value = value

  ElMessage.success('保存成功')
  closeEditDialog()
}

/* -------------------- 删除 -------------------- */

function handleDelete(node: TreeNode) {
  ElMessageBox.confirm(`确定删除「${node.label}」吗？`, '提示', { type: 'warning' })
    .then(() => {
      const removed = removeNodeById(formValue.value.treeData, node.id)
      if (removed) {
        ElMessage.success('删除成功')
      } else {
        ElMessage.error('删除失败')
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
  <el-form-item prop="treeData" :rules="[{ message: '选项必填', blur: 'change', type: 'array', min: 1 }]">
    <template #label>
      <div class="flex-between">
        <span>
          选项
          <span class="color-danger">*</span>
        </span>
        <div class="flex">
          <el-checkbox v-model="formValue.multiple" label="允许多选" size="large" class="pr-8" />
          <el-button link type="primary" @click="openAddRootDialog">
            <MkIcon name="icon_add_outlined" class="mr-4"></MkIcon>
          </el-button>
        </div>
      </div>
    </template>
    <el-card shadow="never" class="border-r-6 w-full" style="--el-card-padding: 8px">
      <el-tree :data="formValue.treeData" node-key="id" default-expand-all :expand-on-click-node="false" :props="treeProps" class="option-tree">
        <template #default="{ data, node }">
          <div class="flex-between w-full">
            <div class="ellipsis" :title="`${data.label}-${data.value}`" style="max-width: 350px">
              <span>{{ data.label }}-{{ data.value }}</span>
            </div>

            <div>
              <span class="mr-4" v-if="node.level < 5">
                <el-button link @click.stop="openAddChildDialog(data)">
                  <MkIcon name="icon_add_outlined" class="color-secondary"></MkIcon>
                </el-button>
              </span>
              <span class="mr-4">
                <el-button link @click.stop="openEditDialog(data)">
                  <MkIcon name="icon_edit_outlined" class="color-secondary"></MkIcon>
                </el-button>
              </span>
              <span>
                <el-button link @click.stop="handleDelete(data)">
                  <MkIcon name="icon_delete-trash_outlined" class="color-secondary"></MkIcon>
                </el-button>
              </span>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>
  </el-form-item>

  <el-form-item class="mk-hide-asterisk" :required="formValue.required" prop="default_value" :rules="formValue.required ? [{ required: true, message: '请输入默认值' }] : []">
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">默认值</span>
        <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
      </div>
    </template>
    <el-tree-select v-model="formValue.default_value" :data="formValue.treeData" :multiple="formValue.multiple" :render-after-expand="false" style="width: 100%" />
  </el-form-item>
  <!-- 添加弹窗 -->
  <el-dialog
    v-model="addDialog.visible"
    :title="addDialog.mode === 'root' ? '添加一级选项' : '添加子选项'"
    width="520px"
    destroy-on-close
    label-position="top"
    require-asterisk-position="right"
    @submit.prevent
  >
    <el-scrollbar>
      <el-row :gutter="8" style="margin-right: 10px" class="tag-list-max-list">
        <template v-for="(item, index) in addDialog.formList" :key="index">
          <el-col :span="12">
            <el-form-item>
              <template #label>
                {{ index === 0 ? '标签' : '' }}
                <span class="color-danger" v-if="index === 0"> *</span>
              </template>
              <el-input v-model.trim="item.label" class="w-full" placeholder="请输入选项标签" maxlength="50"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item class="w-full">
              <template #label>
                {{ index === 0 ? '选项值' : '' }}
                <span class="color-danger" v-if="index === 0">*</span>
              </template>
              <el-input v-model.trim="item.value" placeholder="请输入选项值" maxlength="100"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="1">
            <el-button :disabled="addDialog.formList.length === 1" link @click="removeAddRow(index)" :style="{ marginTop: index === 0 ? '35px' : '12px' }">
              <MkIcon name="icon_delete-trash_outlined"></MkIcon>
            </el-button>
          </el-col>
        </template>
      </el-row>
    </el-scrollbar>
    <el-button link type="primary" @click="appendAddRow">
      <MkIcon name="icon_add_outlined" class="mr-4" />
      添加
    </el-button>
    <template #footer>
      <el-button @click="closeAddDialog">取消</el-button>
      <el-button type="primary" @click="submitAdd">添加</el-button>
    </template>
  </el-dialog>

  <!-- 编辑弹窗 -->
  <el-dialog v-model="editDialog.visible" title="编辑" width="520px" destroy-on-close label-position="top" require-asterisk-position="right" @submit.prevent>
    <el-row :gutter="8">
      <el-col :span="12">
        <el-form-item>
          <template #label>
            标签
            <span class="color-danger"> *</span>
          </template>
          <el-input v-model.trim="editDialog.form.label" placeholder="请输入选项标签" maxlength="50" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item class="w-full">
          <template #label>
            选项值
            <span class="color-danger">*</span>
          </template>
          <el-input v-model.trim="editDialog.form.value" placeholder="请输入选项值" maxlength="100" />
        </el-form-item>
      </el-col>
    </el-row>

    <template #footer>
      <el-button @click="closeEditDialog">取消</el-button>
      <el-button type="primary" @click="submitEdit">保存</el-button>
    </template>
  </el-dialog>
</template>
<style lang="scss" scoped>
.tag-list-max-list {
  max-height: calc(100vh - 260px);
}
</style>
