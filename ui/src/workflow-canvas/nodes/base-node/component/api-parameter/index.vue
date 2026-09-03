<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { Delete, Edit } from '@element-plus/icons-vue'
import { MsgError } from '@/utils/message'
import type { ApiInputField, UserInputField } from '../../types'

defineOptions({ name: 'BaseNodeApiParameter' })

const props = defineProps<{ fields: ApiInputField[]; userFields: UserInputField[] }>()
const emit = defineEmits<{ 'update:fields': [fields: ApiInputField[]] }>()

const dialogVisible = ref(false)
const editingIndex = ref<number>()
const formRef = useTemplateRef<FormInstance>('formRef')
const currentField = ref<ApiInputField>(createField())

function createField(): ApiInputField {
  return { assignment_method: 'api_input', default_value: '', desc: '', is_required: true, type: 'input', variable: '' }
}

function openDialog(field?: ApiInputField, index?: number) {
  editingIndex.value = index
  currentField.value = cloneDeep(field ?? createField())
  dialogVisible.value = true
}

function submitField() {
  formRef.value?.validate().then(() => {
    const field = cloneDeep(currentField.value)
    const duplicated =
      props.fields.some((item, index) => item.variable === field.variable && index !== editingIndex.value) ||
      props.userFields.some(({ field: userField }) => userField === field.variable)
    if (duplicated) {
      MsgError(`参数已存在：${field.variable}`)
      return
    }

    const fields = [...props.fields]
    if (editingIndex.value === undefined) fields.push(field)
    else fields.splice(editingIndex.value, 1, field)
    emit('update:fields', fields)
    dialogVisible.value = false
  })
}

function deleteField(index: number) {
  emit(
    'update:fields',
    props.fields.filter((_field, fieldIndex) => fieldIndex !== index),
  )
}
</script>

<template>
  <section>
    <div class="flex-between mb-3">
      <h6>API 参数</h6>
      <el-button link type="primary" @click="openDialog()"><MkIcon name="icon_add_outlined" />添加</el-button>
    </div>
    <el-table v-if="fields.length" :data="fields" class="mb-4" table-layout="fixed">
      <el-table-column label="参数" prop="variable" min-width="120" show-overflow-tooltip />
      <el-table-column label="描述" prop="desc" min-width="120" show-overflow-tooltip />
      <el-table-column label="默认值" prop="default_value" min-width="100" show-overflow-tooltip />
      <el-table-column label="必填" width="64">
        <template #default="{ row }"><el-switch v-model="row.is_required" disabled size="small" /></template>
      </el-table-column>
      <el-table-column label="操作" width="88">
        <template #default="{ row, $index }">
          <el-button link type="primary" title="编辑" @click="openDialog(row, $index)"><MkIcon :icon="Edit" /></el-button>
          <el-button link type="danger" title="删除" @click="deleteField($index)"><MkIcon :icon="Delete" /></el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>

  <MkDialog v-model="dialogVisible" :title="editingIndex === undefined ? '添加 API 参数' : '编辑 API 参数'" width="560">
    <el-form ref="formRef" :model="currentField" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        label="参数"
        prop="variable"
        :rules="[
          { required: true, message: '请输入参数', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字和下划线', trigger: 'blur' },
        ]"
      >
        <el-input v-model="currentField.variable" maxlength="64" show-word-limit @blur="currentField.variable = currentField.variable.trim()" />
      </el-form-item>
      <el-form-item label="描述"><el-input v-model="currentField.desc" maxlength="64" show-word-limit /></el-form-item>
      <el-form-item label="是否必填"><el-switch v-model="currentField.is_required" size="small" /></el-form-item>
      <el-form-item label="默认值" prop="default_value" :rules="{ required: currentField.is_required, message: '请输入默认值', trigger: 'blur' }">
        <el-input v-model="currentField.default_value" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
