<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { MkDynamicsFormConstructor, dynamicFormTypeOptions, type FormField } from '@/components/mk-dynamics-form'

const emit = defineEmits<{ submit: [data: FormField, index?: number] }>()
const constructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const currentField = ref<Partial<FormField>>(createField())
const allowedInputTypes = ['TextInput', 'PasswordInput', 'SingleSelect', 'MultiSelect', 'RadioCard', 'DatePicker', 'SwitchInput']
const fieldTypeOptions = dynamicFormTypeOptions
  .filter(({ value }) => allowedInputTypes.includes(value))
  .map(({ label, value }) => ({ label, value: `${value}Constructor` }))

function createField(): Partial<FormField> {
  return { input_type: 'TextInput', required: false, attrs: { maxlength: 200, minlength: 0 }, show_default_value: true }
}

// 兼容旧版 input/select/date 字段，已使用动态表单协议的配置直接保留。
function normalizeField(field: FormField): FormField {
  const draft = cloneDeep(field)
  if (draft.input_type) return draft
  const common = {
    ...draft,
    field: draft.field || draft.variable || '',
    label: draft.label || draft.name,
    required: draft.required ?? draft.is_required,
  }
  if (draft.type === 'select') {
    const options = (draft.optionList ?? []) as string[]
    return {
      ...common,
      input_type: 'SingleSelect',
      attrs: draft.attrs ?? {},
      option_list: draft.option_list ?? options.map((value) => ({ key: value, value })),
    }
  }
  if (draft.type === 'date') {
    return {
      ...common,
      input_type: 'DatePicker',
      attrs: { format: 'YYYY-MM-DD HH:mm:ss', 'value-format': 'YYYY-MM-DD HH:mm:ss', type: 'datetime', ...draft.attrs },
    }
  }
  return { ...common, input_type: 'TextInput', attrs: draft.attrs ?? { maxlength: 200, minlength: 0 } }
}

function resetData() {
  currentField.value = createField()
  editingIndex.value = undefined
}

function open(field?: FormField, index?: number) {
  resetData()
  if (field) currentField.value = normalizeField(field)
  editingIndex.value = index
  dialogVisible.value = true
}

function submitField() {
  const constructor = constructorRef.value
  if (!constructor) return
  constructor
    .validate()
    .then(() => emit('submit', cloneDeep(constructor.getData()), editingIndex.value))
    .catch(() => {})
}

function close() {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="editingIndex === undefined ? '添加参数' : '编辑参数'" align-center @closed="resetData">
    <MkDynamicsFormConstructor ref="constructorRef" v-model="currentField" :field-type-options="fieldTypeOptions" />
    <template #footer>
      <!-- 取消编辑 -->
      <el-button @click="close">取消</el-button>
      <!-- 提交参数 -->
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
