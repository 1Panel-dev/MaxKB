<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { MkDynamicsFormConstructor, type FormField, type VisibilityFieldOption } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'

const props = defineProps<{ formFields: FormField[]; nodeId: string }>()
const emit = defineEmits<{ submit: [data: FormField, index?: number] }>()
const fieldDialogVisible = ref(false)
const editingIndex = ref<number>()
const constructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')
const currentField = ref<Partial<FormField>>(createField())

const visibilityOptions = computed<VisibilityFieldOption[]>(() => [
  {
    children: props.formFields
      .filter((_field, index) => index !== editingIndex.value)
      .map((field) => ({
        attrs: field.attrs,
        input_type: field.input_type,
        label: formatLabel(field.label, field.field),
        option_list: field.option_list,
        value: field.field,
      })),
    label: '当前表单',
    self: true,
    value: props.nodeId,
  },
])

function formatLabel(label: FormField['label'], fallback = '') {
  return typeof label === 'string' ? label : (label?.label ?? fallback)
}

function createField(): Partial<FormField> {
  return { input_type: 'TextInput', required: false, show_default_value: true }
}

function open(field?: FormField, index?: number) {
  if (field) currentField.value = cloneDeep(field)
  editingIndex.value = index
  fieldDialogVisible.value = true
}

function submitField() {
  const constructor = constructorRef.value
  if (!constructor) return
  constructor
    .validate()
    .then(() => {
      const field = constructor.getData()
      if (!field.field || !/^[a-zA-Z0-9_]+$/.test(field.field)) {
        MsgError('参数仅支持字母、数字和下划线')
        return
      }
      emit('submit', cloneDeep(field), editingIndex.value)
    })
    .catch(() => {})
}

function resetData() {
  editingIndex.value = undefined
  currentField.value = createField()
}
function close() {
  fieldDialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="fieldDialogVisible" :title="editingIndex === undefined ? '添加参数' : '编辑参数'" align-center @closed="resetData">
    <MkDynamicsFormConstructor ref="constructorRef" v-model="currentField" enable-visibility :left-options="visibilityOptions" />
    <template #footer>
      <el-button @click="fieldDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
