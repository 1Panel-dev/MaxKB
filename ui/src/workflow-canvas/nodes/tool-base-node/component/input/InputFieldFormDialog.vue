<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { cloneDeep } from 'lodash'
import type { ToolInputField } from '../../types'

const typeOptions = ['string', 'int', 'dict', 'array', 'float', 'boolean']
const emit = defineEmits<{ submit: [data: ToolInputField, index?: number] }>()
const formRef = useTemplateRef<FormInstance>('formRef')
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const form = ref<ToolInputField>(createField())
const rules: FormRules<ToolInputField> = {
  field: [{ required: true, message: '请输入参数', trigger: 'blur' }],
  label: [{ required: true, message: '请输入显示名', trigger: 'blur' }],
}

function createField(): ToolInputField {
  return { field: '', type: 'string', label: '', desc: '', is_required: true }
}

// 打开和关闭统一重置草稿，取消编辑不会影响下一次添加。
function resetData() {
  form.value = createField()
  editingIndex.value = undefined
  formRef.value?.clearValidate()
}

function open(field?: ToolInputField, index?: number) {
  resetData()
  if (field) form.value = cloneDeep(field)
  editingIndex.value = index
  dialogVisible.value = true
}

function submitField() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(form.value), editingIndex.value))
    .catch(() => {})
}

function close() {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="editingIndex === undefined ? '添加参数' : '编辑参数'" align-center @closed="resetData">
    <el-form label-position="top" ref="formRef" :rules="rules" :model="form" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="参数" prop="field">
        <el-input v-model="form.field" placeholder="请输入参数" :maxlength="64" show-word-limit @blur="form.field = form.field.trim()" />
      </el-form-item>
      <el-form-item label="显示名称" prop="label">
        <el-input v-model="form.label" placeholder="请输入显示名称" :maxlength="128" show-word-limit @blur="form.label = form.label?.trim()" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.desc" placeholder="请输入描述" :maxlength="128" show-word-limit @blur="form.desc = form.desc?.trim()" />
      </el-form-item>
      <el-form-item label="数据类型">
        <el-select v-model="form.type">
          <el-option v-for="fieldType in typeOptions" :key="fieldType" :label="fieldType" :value="fieldType" />
        </el-select>
      </el-form-item>

      <el-form-item label="必填">
        <el-switch size="small" v-model="form.is_required" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span>
        <!-- 取消编辑 -->
        <el-button @click="dialogVisible = false">取消</el-button>
        <!-- 提交参数 -->
        <el-button type="primary" @click="submitField">
          {{ editingIndex === undefined ? '添加' : '保存' }}
        </el-button>
      </span>
    </template>
  </MkDialog>
</template>
