<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ChatInputField } from '../../types'

const emit = defineEmits<{ submit: [data: ChatInputField, index?: number] }>()
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const formRef = useTemplateRef<FormInstance>('formRef')
const currentField = ref<ChatInputField>(createField())

function createField(): ChatInputField {
  return { field: '', label: '' }
}

function open(field?: ChatInputField, index?: number) {
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
        prop="field"
        :rules="[
          { required: true, message: '请输入参数', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字和下划线', trigger: 'blur' },
        ]"
      >
        <el-input
          v-model="currentField.field"
          maxlength="64"
          show-word-limit
          placeholder="请输入参数"
          @blur="currentField.field = currentField.field.trim()"
        />
      </el-form-item>
      <el-form-item label="显示名称" prop="label" :rules="{ required: true, message: '请输入显示名称', trigger: 'blur' }">
        <el-input v-model="currentField.label" maxlength="64" show-word-limit placeholder="请输入显示名称" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
