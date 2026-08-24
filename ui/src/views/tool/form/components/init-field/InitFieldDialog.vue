<script setup lang="ts">
import { nextTick, reactive, ref, toRaw } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ToolInitField } from '@/api/types'

defineOptions({ name: 'InitFieldDialog' })

const emit = defineEmits<{
  refresh: [field: ToolInitField]
}>()

const initFieldTypeOptions = [
  { label: '文本框', value: 'TextInput' },
  { label: '密码框', value: 'PasswordInput' },
  { label: 'JSON 输入框', value: 'JsonInput' },
  { label: '开关', value: 'SwitchInput' },
]

const formRef = ref<FormInstance>()
const visible = ref(false)
const isEdit = ref(false)
const initFieldForm = reactive<ToolInitField>({
  default_value: '',
  field: '',
  input_type: 'TextInput',
  label: '',
  required: false,
  show_default_value: true,
})
const formRules: FormRules<ToolInitField> = {
  field: [{ required: true, message: '请输入变量名', trigger: 'blur' }],
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
}

function open(field?: ToolInitField) {
  if (field) {
    isEdit.value = true
    Object.assign(initFieldForm, structuredClone(toRaw(field)))
  }

  visible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function resetData() {
  isEdit.value = false
  Object.assign(initFieldForm, {
    default_value: '',
    field: '',
    input_type: 'TextInput',
    label: '',
    required: false,
    show_default_value: true,
  })
  formRef.value?.clearValidate()
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    emit('refresh', structuredClone(toRaw(initFieldForm)))
    visible.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="isEdit ? '编辑参数' : '添加参数'" @closed="resetData">
    <el-form
      ref="formRef"
      :model="initFieldForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="变量名" prop="field">
        <el-input v-model="initFieldForm.field" maxlength="64" placeholder="请输入变量名" />
      </el-form-item>
      <el-form-item label="显示名称" prop="label">
        <el-input v-model="initFieldForm.label" maxlength="64" placeholder="请输入显示名称" />
      </el-form-item>
      <el-form-item label="组件类型">
        <el-select v-model="initFieldForm.input_type" class="w-full">
          <el-option
            v-for="option in initFieldTypeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="默认值">
        <el-switch
          v-if="initFieldForm.input_type === 'SwitchInput'"
          v-model="initFieldForm.default_value"
        />
        <el-input
          v-else
          v-model="initFieldForm.default_value as string"
          :show-password="initFieldForm.input_type === 'PasswordInput'"
          :type="initFieldForm.input_type === 'JsonInput' ? 'textarea' : 'text'"
          placeholder="请输入默认值"
        />
      </el-form-item>
      <el-form-item label="必填"><el-switch v-model="initFieldForm.required" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ isEdit ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
