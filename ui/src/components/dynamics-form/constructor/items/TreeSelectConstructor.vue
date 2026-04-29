<template>
  <el-form-item
    prop="treeData"
    :rules="[
      {
        message: $t('dynamicsForm.TreeSelect.selectRequired'),
        blur: 'change',
        type: 'array',
        min: 1,
      },
    ]"
  >
    <template #label>
      <div class="flex-between">
        <span>
          {{ $t('dynamicsForm.TreeSelect.select') }}
          <span class="color-danger">*</span>
        </span>
        <div class="flex">
          <el-checkbox
            v-model="formValue.multiple"
            :label="$t('dynamicsForm.TreeSelect.allowMultipleSelections')"
            size="large"
            class="pr-8"
          />
          <el-button link type="primary" @click="openAddRootDialog">
            <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
          </el-button>
        </div>
      </div>
    </template>
    <el-card shadow="never" class="border-r-6 w-full" style="--el-card-padding: 8px">
      <el-tree
        :data="formValue.treeData"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        :props="treeProps"
        class="option-tree"
      >
        <template #default="{ data, node }">
          <div class="flex-between w-full">
            <div class="ellipsis" :title="`${data.label}-${data.value}`" style="max-width: 350px">
              <span>{{ data.label }}-{{ data.value }}</span>
            </div>

            <div>
              <span class="mr-4" v-if="node.level < 5">
                <el-button link @click.stop="openAddChildDialog(data)">
                  <AppIcon iconName="app-add-outlined" class="color-secondary"></AppIcon>
                </el-button>
              </span>
              <span class="mr-4">
                <el-button link @click.stop="openEditDialog(data)">
                  <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                </el-button>
              </span>
              <span>
                <el-button link @click.stop="handleDelete(data)">
                  <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                </el-button>
              </span>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>
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
      :data="formValue.treeData"
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
                {{ index === 0 ? $t('dynamicsForm.tag.label') : '' }}
                <span class="color-danger" v-if="index === 0"> *</span>
              </template>
              <el-input
                v-model.trim="item.label"
                class="w-full"
                :placeholder="$t('dynamicsForm.tag.placeholder')"
                maxlength="50"
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item class="w-full">
              <template #label>
                {{ index === 0 ? $t('dynamicsForm.Select.label') : '' }}
                <span class="color-danger" v-if="index === 0">*</span>
              </template>
              <el-input
                v-model.trim="item.value"
                :placeholder="$t('dynamicsForm.Select.placeholder')"
                maxlength="100"
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="1">
            <el-button
              :disabled="addDialog.formList.length === 1"
              link
              @click="removeAddRow(index)"
              :style="{ marginTop: index === 0 ? '35px' : '12px' }"
            >
              <AppIcon iconName="app-delete"></AppIcon>
            </el-button>
          </el-col>
        </template>
      </el-row>
    </el-scrollbar>
    <el-button link type="primary" @click="appendAddRow">
      <AppIcon iconName="app-add-outlined" class="mr-4" />
      {{ $t('common.add') }}
    </el-button>
    <template #footer>
      <el-button @click="closeAddDialog">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submitAdd">{{ $t('common.add') }}</el-button>
    </template>
  </el-dialog>

  <!-- 编辑弹窗 -->
  <el-dialog
    v-model="editDialog.visible"
    :title="$t('common.edit')"
    width="520px"
    destroy-on-close
    label-position="top"
    require-asterisk-position="right"
    @submit.prevent
  >
    <el-row :gutter="8">
      <el-col :span="12">
        <el-form-item>
          <template #label>
            {{ $t('dynamicsForm.tag.label') }}
            <span class="color-danger"> *</span>
          </template>
          <el-input
            v-model.trim="editDialog.form.label"
            :placeholder="$t('dynamicsForm.tag.placeholder')"
            maxlength="50"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item class="w-full">
          <template #label>
            {{ $t('dynamicsForm.Select.label') }}
            <span class="color-danger">*</span>
          </template>
          <el-input
            v-model.trim="editDialog.form.value"
            :placeholder="$t('dynamicsForm.Select.placeholder')"
            maxlength="100"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <template #footer>
      <el-button @click="closeEditDialog">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submitEdit">{{ $t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'
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
    attrs: { multiple: formValue.value.multiple, data: formValue.value.treeData, filterable: true },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
  }
}
const rander = (form_data: any) => {
  const attrs = form_data.attrs || {}
  formValue.value.multiple = attrs.multiple
  formValue.value.treeData = attrs.data || []
  formValue.value.default_value = form_data.default_value
  formValue.value.show_default_value = form_data.show_default_value
}

defineExpose({ getData, rander })
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

const treeProps = {
  children: 'children',
  label: 'label',
}

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
    formValue.value.treeData.push(...newNodes)
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
      const removed = removeNodeById(formValue.value.treeData, node.id)
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
.tag-list-max-list {
  max-height: calc(100vh - 260px);
}
</style>
