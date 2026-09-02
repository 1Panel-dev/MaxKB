<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type { ToolInputField, ToolInputFieldType } from '@/api/types'

defineOptions({ name: 'WorkflowToolInputFieldDialog' })

const emit = defineEmits<{ refresh: [field: ToolInputField] }>()

const inputFieldTypes: ToolInputFieldType[] = ['string', 'int', 'float', 'dict', 'array']
const formRef = ref<FormInstance>()
const visible = ref(false)
const editing = ref(false)
const inputFieldForm = reactive<ToolInputField>({ desc: '', is_required: true, name: '', source: 'reference', type: 'string' })
const formRules: FormRules<ToolInputField> = {
  name: [{ required: true, message: '请输入参数名称', trigger: 'blur' }],
}

function open(field?: ToolInputField) {
  editing.value = Boolean(field)
  if (field) Object.assign(inputFieldForm, cloneDeep(field))
  visible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    emit('refresh', cloneDeep(inputFieldForm))
    visible.value = false
  })
}

function resetData() {
  editing.value = false
  Reflect.deleteProperty(inputFieldForm, 'value')
  Object.assign(inputFieldForm, { desc: '', is_required: true, name: '', source: 'reference', type: 'string' })
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="editing ? '编辑参数' : '添加参数'" width="500" @closed="resetData">
    <el-form ref="formRef" :model="inputFieldForm" :rules="formRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="参数名称" prop="name">
        <el-input
          v-model="inputFieldForm.name"
          maxlength="64"
          placeholder="请输入参数名称"
          @blur="inputFieldForm.name = inputFieldForm.name.trim()"
        />
      </el-form-item>
      <el-form-item label="数据类型">
        <el-select v-model="inputFieldForm.type" class="w-full">
          <el-option v-for="fieldType in inputFieldTypes" :key="fieldType" :label="fieldType" :value="fieldType" />
        </el-select>
      </el-form-item>
      <el-form-item label="参数说明">
        <el-input
          v-model="inputFieldForm.desc"
          maxlength="128"
          placeholder="请输入参数说明"
          show-word-limit
          @blur="inputFieldForm.desc = inputFieldForm.desc?.trim()"
        />
      </el-form-item>
      <el-form-item label="来源">
        <el-select v-model="inputFieldForm.source" class="w-full">
          <el-option label="引用参数" value="reference" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否必填" @click.prevent>
        <el-switch v-model="inputFieldForm.is_required" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ editing ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
