<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type { ParameterField } from './types'

defineOptions({ name: 'ParameterExtractionFieldDialog' })

const emit = defineEmits<{ submit: [data: ParameterField, index?: number] }>()

const parameterTypeOptions = ['string', 'number', 'object', 'boolean', 'array'].map((type) => ({ value: type, label: type }))
const formRef = useTemplateRef<FormInstance>('formRef')
const editing = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const formData = ref<ParameterField>({ field: '', label: '', parameter_type: '', desc: '' })

const rules: FormRules<ParameterField> = {
  field: [
    { required: true, message: '请输入参数', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '参数可由字母、数字、下划线组成', trigger: 'blur' },
  ],
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  parameter_type: [{ required: true, message: '请选择参数类型', trigger: 'change' }],
}

const visible = ref(false)

function open(data?: ParameterField, index?: number) {
  resetData()
  if (data) {
    formData.value = cloneDeep(data)
    editing.value = true
    currentIndex.value = index
  }
  visible.value = true
}

function handleSubmit() {
  formRef.value
    ?.validate()
    .then(() => {
      emit('submit', cloneDeep(formData.value), currentIndex.value)
    })
    .catch(() => {})
}

function close() {
  visible.value = false
}

function resetData() {
  editing.value = false
  currentIndex.value = undefined
  formData.value = { field: '', label: '', parameter_type: '', desc: '' }
  formRef.value?.clearValidate()
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog v-model="visible" :title="editing ? '编辑参数' : '添加参数'" @closed="resetData" align-center>
    <el-form ref="formRef" label-position="top" require-asterisk-position="right" :rules="rules" :model="formData" @submit.prevent>
      <el-form-item label="参数" prop="field">
        <el-input v-model="formData.field" :maxlength="64" placeholder="请输入参数" show-word-limit />
      </el-form-item>
      <el-form-item label="显示名称" prop="label">
        <el-input v-model="formData.label" :maxlength="64" placeholder="请输入显示名称" show-word-limit />
      </el-form-item>
      <el-form-item label="参数类型" prop="parameter_type">
        <el-select v-model="formData.parameter_type" placeholder="请选择参数类型" class="w-full">
          <el-option v-for="item in parameterTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述" prop="desc">
        <el-input v-model="formData.desc" type="textarea" :rows="3" placeholder="请输入描述" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ editing ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
