<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import { TRIGGER_BODY_TYPE } from '@/api/enums'
import type { TriggerBodyField } from '@/api/types'

const props = defineProps<{ fields: TriggerBodyField[] }>()
const emit = defineEmits<{ submit: [field: TriggerBodyField, index?: number] }>()
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const editingIndex = ref<number>()
const createDefaultField = (): TriggerBodyField => ({ field: '', type: TRIGGER_BODY_TYPE.STRING, desc: '', required: false })
const formData = ref<TriggerBodyField>(createDefaultField())
const rules: FormRules<TriggerBodyField> = {
  field: [
    { required: true, whitespace: true, message: '请输入参数名', trigger: 'blur' },
    {
      validator: (_rule, value: string, callback) => {
        const duplicate = props.fields.some((field, index) => index !== editingIndex.value && field.field.trim() === value.trim())
        callback(duplicate ? new Error('参数名称不能重复') : undefined)
      },
      trigger: 'blur',
    },
  ],
  type: [{ required: true, message: '请选择参数类型', trigger: 'change' }],
}

function open(field?: TriggerBodyField, index?: number) {
  editingIndex.value = index
  formData.value = field ? cloneDeep(field) : createDefaultField()
  formRef.value?.clearValidate()
  visible.value = true
}
function close() {
  visible.value = false
}
function resetData() {
  formData.value = createDefaultField()
  editingIndex.value = undefined
  formRef.value?.clearValidate()
}
function submit() {
  formData.value.field = formData.value.field.trim()
  formRef.value?.validate((valid) => {
    if (valid) emit('submit', cloneDeep(formData.value), editingIndex.value)
  })
}
defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="editingIndex === undefined ? '添加请求参数' : '编辑请求参数'" @closed="resetData">
    <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="参数名" prop="field">
        <el-input v-model="formData.field" placeholder="请输入参数名" />
      </el-form-item>
      <el-form-item label="类型" prop="type">
        <el-select v-model="formData.type" placeholder="请选择参数类型">
          <el-option v-for="type in TRIGGER_BODY_TYPE" :key="type" :label="type" :value="type" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述" prop="desc">
        <el-input v-model="formData.desc" type="textarea" :rows="3" placeholder="请输入描述" />
      </el-form-item>
      <el-form-item prop="required" class="mb-0!">
        <el-checkbox v-model="formData.required">必填</el-checkbox>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消请求参数编辑 -->
      <el-button plain @click="close">取消</el-button>
      <!-- 确认请求参数 -->
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
