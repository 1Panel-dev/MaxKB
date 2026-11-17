<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { DynamicFormConstructorOption, FormField } from '@/components/mk-dynamics-form'
import { DYNAMIC_FORM_TYPES, MkDynamicsFormConstructor } from '@/components/mk-dynamics-form'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'InitFieldDialog' })

const emit = defineEmits<{ submit: [field: FormField] }>()

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
const initFieldTypeOptions = computed<DynamicFormConstructorOption[]>(() =>
  initFieldInputTypes.map((inputType) => {
    const definition = DYNAMIC_FORM_TYPES.find(({ value }) => value === inputType)
    return { label: definition ? t(definition.labelKey) : inputType, value: `${inputType}Constructor` }
  }),
)

const visible = ref(false)
const editing = ref(false)
const currentField = ref<Partial<FormField>>(createDefaultField())
const constructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')

function createDefaultField(): Partial<FormField> {
  return { attrs: { maxlength: 200, minlength: 0 }, input_type: 'TextInput', required: false, show_default_value: true }
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
  <MkDialog v-model="visible" :title="editing ? t('common.parameters.edit') : t('common.parameters.add')" @closed="resetData">
    <MkDynamicsFormConstructor ref="constructorRef" v-model="currentField" :field-type-options="initFieldTypeOptions" />

    <template #footer>
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" @click="handleSubmit">
        {{ editing ? t('common.actions.save') : t('common.actions.add') }}
      </el-button>
    </template>
  </MkDialog>
</template>
