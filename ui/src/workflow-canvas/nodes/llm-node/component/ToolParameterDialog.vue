<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import { toolParameterTypes, type LlmToolParameter } from '../types'

defineOptions({ name: 'WorkflowLlmToolParameterDialog' })

const emit = defineEmits<{ submit: [parameter: LlmToolParameter, index?: number] }>()
const formRef = useTemplateRef<FormInstance>('formRef')
const visible = ref(false)
const currentIndex = ref<number>()
const formData = ref<LlmToolParameter>(createParameter())
const rules: FormRules<LlmToolParameter> = {
  name: [{ whitespace: true, required: true, message: '请输入参数', trigger: 'blur' }],
  type: [{ required: true, message: '请选择数据类型', trigger: 'change' }],
}

function createParameter(): LlmToolParameter {
  return { name: '', type: 'string', description: '', required: true }
}

function open(parameter?: LlmToolParameter, index?: number) {
  if (parameter) formData.value = cloneDeep(parameter)
  currentIndex.value = index
  visible.value = true
}

function close() {
  visible.value = false
}

function handleSubmit() {
  formData.value.name = formData.value.name.trim()
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(formData.value), currentIndex.value))
    .catch(() => {})
}

function resetData() {
  formData.value = createParameter()
  currentIndex.value = undefined
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="currentIndex === undefined ? '添加工具参数' : '编辑工具参数'" @closed="resetData">
    <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent @paste.stop>
      <el-form-item label="参数" prop="name">
        <el-input v-model="formData.name" maxlength="64" show-word-limit placeholder="请输入参数" @blur="formData.name = formData.name.trim()" />
      </el-form-item>
      <el-form-item label="数据类型" prop="type">
        <el-select v-model="formData.type" placeholder="请选择数据类型" class="w-full">
          <el-option v-for="parameterType in toolParameterTypes" :key="parameterType" :label="parameterType" :value="parameterType" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="formData.description" type="textarea" :rows="3" maxlength="256" show-word-limit placeholder="请输入描述" />
      </el-form-item>
      <el-form-item label="是否必填">
        <el-switch v-model="formData.required" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消参数编辑 -->
      <el-button plain @click="close">取消</el-button>
      <!-- 保存工具参数 -->
      <el-button type="primary" @click="handleSubmit">保存</el-button>
    </template>
  </MkDialog>
</template>
