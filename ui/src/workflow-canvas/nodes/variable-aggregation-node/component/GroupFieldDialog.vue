<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'VariableAggregationGroupFieldDialog' })

interface GroupFieldForm {
  field: string
  label: string
}

const emit = defineEmits<{ submit: [data: GroupFieldForm, index?: number] }>()

const formRef = useTemplateRef<FormInstance>('formRef')
const editing = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const formData = ref<GroupFieldForm>({ field: '', label: '' })

const rules: FormRules<GroupFieldForm> = {
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  field: [
    { required: true, message: '请输入变量', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '变量可由字母、数字、下划线组成', trigger: 'blur' },
  ],
}

const visible = ref(false)

function open(data?: GroupFieldForm, index?: number) {
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
  formData.value = { field: '', label: '' }
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog v-model="visible" :title="editing ? '编辑分组' : '添加分组'" @closed="resetData" align-center>
    <el-form ref="formRef" label-position="top" require-asterisk-position="right" :rules="rules" :model="formData" @submit.prevent="handleSubmit">
      <el-form-item label="变量" prop="field">
        <el-input v-model="formData.field" :maxlength="64" placeholder="请输入变量" show-word-limit />
      </el-form-item>
      <el-form-item label="显示名称" prop="label">
        <el-input v-model="formData.label" :maxlength="64" show-word-limit placeholder="请输入显示名称" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ editing ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
