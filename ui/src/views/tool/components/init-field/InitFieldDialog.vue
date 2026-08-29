<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import {
  dynamicFormTypeOptions,
  MkDynamicsFormConstructor,
  type DynamicFormConstructorOption,
  type FormField,
} from '@/components/mk-dynamics-form'

defineOptions({ name: 'InitFieldDialog' })

const emit = defineEmits<{
  submit: [field: FormField]
}>()

const initFieldInputTypes = [
  'TextInput',
  'Slider',
  'PasswordInput',
  'SingleSelect',
  'MultiSelect',
  'RadioCard',
  'DatePicker',
  'SwitchInput',
  'JsonInput',
] as const
const initFieldTypeOptions: DynamicFormConstructorOption[] = initFieldInputTypes.map(
  (inputType) => ({
    label: dynamicFormTypeOptions.find((option) => option.value === inputType)?.label ?? inputType,
    value: `${inputType}Constructor`,
  }),
)

const visible = ref(false)
const editing = ref(false)
const currentField = ref<Partial<FormField>>(createDefaultField())
const constructorRef =
  useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')

function createDefaultField(): Partial<FormField> {
  return {
    attrs: { maxlength: 200, minlength: 0 },
    input_type: 'TextInput',
    required: false,
    show_default_value: true,
  }
}

function resetData() {
  editing.value = false
  currentField.value = createDefaultField()
}

function open(field?: FormField) {
  if (field) {
    editing.value = true
    currentField.value = cloneDeep(field)
  }
  visible.value = true
}

function handleSubmit() {
  constructorRef.value?.validate().then(() => {
    const field = constructorRef.value?.getData()
    if (!field) return

    emit('submit', field)
    visible.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    align-center
    :title="editing ? '编辑参数' : '添加参数'"
    @closed="resetData"
  >
    <MkDynamicsFormConstructor
      ref="constructorRef"
      v-model="currentField"
      :field-type-options="initFieldTypeOptions"
    />

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">
        {{ editing ? '保存' : '添加' }}
      </el-button>
    </template>
  </MkDialog>
</template>
