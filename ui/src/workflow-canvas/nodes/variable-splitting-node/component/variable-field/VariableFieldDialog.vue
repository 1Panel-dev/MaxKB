<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { cloneDeep } from 'lodash'
import type { VariableField } from './types'

defineOptions({ name: 'VariableSplittingFieldDialog' })

const emit = defineEmits<{ submit: [data: VariableField, index?: number] }>()

const formRef = useTemplateRef<FormInstance>('formRef')
const editing = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const formData = ref<VariableField>({ field: '', label: '', expression: '' })

const rules: FormRules<VariableField> = {
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  field: [
    { required: true, message: '请输入变量', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '变量可由字母、数字、下划线组成', trigger: 'blur' },
  ],
  expression: [{ required: true, message: '请输入表达式', trigger: 'blur' }],
}

const visible = ref(false)

function open(data?: VariableField, index?: number) {
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
  formData.value = { field: '', label: '', expression: '' }
  formRef.value?.clearValidate()
}

defineExpose({ close, open })
</script>
<template>
  <MkDialog v-model="visible" :title="editing ? '编辑变量' : '添加变量'" @closed="resetData" align-center>
    <el-form ref="formRef" label-position="top" require-asterisk-position="right" :rules="rules" :model="formData" @submit.prevent>
      <el-form-item label="变量" prop="field">
        <el-input v-model="formData.field" :maxlength="64" placeholder="请输入变量" show-word-limit />
      </el-form-item>
      <el-form-item label="显示名称" prop="label">
        <el-input v-model="formData.label" :maxlength="64" show-word-limit placeholder="请输入显示名称" />
      </el-form-item>
      <el-form-item class="mk-hide-asterisk" prop="expression">
        <template #label>
          <span class="flex items-center gap-1">
            <span class="mk-required">表达式</span>
            <el-tooltip placement="right">
              <template #content>
                请使用 JSON Path 表达式拆分变量，例如：$.store.book
                <a
                  href="https://pypi.org/project/jsonpath-ng/1.8.0/"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:text-primary/80"
                  >点击查看详情 ➜ pypi.org</a
                >
              </template>
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
        </template>
        <el-input v-model="formData.expression" :maxlength="64" show-word-limit placeholder="请输入表达式" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ editing ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
