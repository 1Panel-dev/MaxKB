<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ApiInputField } from '../../types'

const emit = defineEmits<{ submit: [data: ApiInputField, index?: number] }>()
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const formRef = useTemplateRef<FormInstance>('formRef')
const currentField = ref<ApiInputField>(createField())

function createField(): ApiInputField {
  return { assignment_method: 'api_input', default_value: '', desc: '', is_required: true, type: 'input', variable: '' }
}

function open(field?: ApiInputField, index?: number) {
  if (field) currentField.value = cloneDeep(field)
  editingIndex.value = index
  dialogVisible.value = true
}

function submitField() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(currentField.value), editingIndex.value))
    .catch(() => {})
}

function resetData() {
  editingIndex.value = undefined
  currentField.value = createField()
  formRef.value?.clearValidate()
}

function close() {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="editingIndex === undefined ? '添加参数' : '编辑参数'" align-center @closed="resetData">
    <el-form ref="formRef" :model="currentField" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        label="参数"
        prop="variable"
        :rules="[
          { required: true, message: '请输入参数', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字和下划线', trigger: 'blur' },
        ]"
      >
        <el-input
          v-model="currentField.variable"
          maxlength="64"
          show-word-limit
          @blur="currentField.variable = currentField.variable.trim()"
          placeholder="请输入参数"
        />
      </el-form-item>
      <el-form-item label="描述"><el-input v-model="currentField.desc" maxlength="64" show-word-limit placeholder="请输入描述" /></el-form-item>
      <el-form-item label="是否必填"><el-switch v-model="currentField.is_required" size="small" /></el-form-item>
      <el-form-item label="默认值" prop="default_value" :rules="{ required: currentField.is_required, message: '请输入默认值', trigger: 'blur' }">
        <el-input v-model="currentField.default_value" placeholder="请输入默认值" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
