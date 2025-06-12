<template>
  <el-dialog
    :title="
      isEdit
        ? $t('common.param.editParam')
        : $t('common.param.addParam')
    "
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <DynamicsFormConstructor
      v-model="currentRow"
      label-position="top"
      require-asterisk-position="right"
      :input_type_list="inputTypeList"
      ref="DynamicsFormConstructorRef"
    ></DynamicsFormConstructor>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="close"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ isEdit ? $t('common.save') : $t('common.add') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { cloneDeep } from 'lodash'
import DynamicsFormConstructor from '@/components/dynamics-form/constructor/index.vue'
import type { FormField } from '@/components/dynamics-form/type'
import _ from 'lodash'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const DynamicsFormConstructorRef = ref()
const loading = ref<boolean>(false)
const isEdit = ref(false)
const currentItem = ref<FormField | any>()
const check_field = (field_list: Array<string>, obj: any) => {
  return field_list.every((field) => _.get(obj, field, undefined) !== undefined)
}
const currentRow = computed(() => {
  if (currentItem.value) {
    const row = currentItem.value
    switch (row.type) {
      case 'input':
        if (check_field(['field', 'input_type', 'label', 'required', 'attrs'], currentItem.value)) {
          return currentItem.value
        }
        return {
          attrs: row.attrs || { maxlength: 200, minlength: 0 },
          field: row.field || row.variable,
          input_type: 'TextInput',
          label: row.label || row.name,
          default_value: row.default_value,
          required: row.required != undefined ? row.required : row.is_required
        }
      case 'select':
        if (
          check_field(
            ['field', 'input_type', 'label', 'required', 'option_list'],
            currentItem.value
          )
        ) {
          return currentItem.value
        }
        return {
          attrs: row.attrs || {},
          field: row.field || row.variable,
          input_type: 'SingleSelect',
          label: row.label || row.name,
          default_value: row.default_value,
          required: row.required != undefined ? row.required : row.is_required,
          option_list: row.option_list
            ? row.option_list
            : row.optionList.map((o: any) => {
                return { key: o, value: o }
              })
        }

      case 'date':
        if (
          check_field(
            [
              'field',
              'input_type',
              'label',
              'required',
              'attrs.format',
              'attrs.value-format',
              'attrs.type'
            ],
            currentItem.value
          )
        ) {
          return currentItem.value
        }
        return {
          field: row.field || row.variable,
          input_type: 'DatePicker',
          label: row.label || row.name,
          default_value: row.default_value,
          required: row.required != undefined ? row.required : row.is_required,
          attrs: {
            format: 'YYYY-MM-DD HH:mm:ss',
            'value-format': 'YYYY-MM-DD HH:mm:ss',
            type: 'datetime'
          }
        }
      default:
        return currentItem.value
    }
  } else {
    return { input_type: 'TextInput', required: false, attrs: { maxlength: 200, minlength: 0 }, show_default_value: true }
  }
})
const currentIndex = ref(null)
const inputTypeList = ref([
  { label: t('dynamicsForm.input_type_list.TextInput'), value: 'TextInputConstructor' },
  { label: t('dynamicsForm.input_type_list.PasswordInput'), value: 'PasswordInputConstructor' },
  { label: t('dynamicsForm.input_type_list.SingleSelect'), value: 'SingleSelectConstructor' },
  { label: t('dynamicsForm.input_type_list.MultiSelect'), value: 'MultiSelectConstructor' },
  { label: t('dynamicsForm.input_type_list.RadioCard'), value: 'RadioCardConstructor' },
  { label: t('dynamicsForm.input_type_list.DatePicker'), value: 'DatePickerConstructor' },
  { label: t('dynamicsForm.input_type_list.SwitchInput'), value: 'SwitchInputConstructor' },
])

const dialogVisible = ref<boolean>(false)

const open = (row: any, index: any) => {
  dialogVisible.value = true

  if (row) {
    isEdit.value = true
    currentItem.value = cloneDeep(row)
    currentIndex.value = index
  } else {
    currentItem.value = null
  }
}

const close = () => {
  dialogVisible.value = false
  isEdit.value = false
  currentIndex.value = null
  currentItem.value = null as any
}

const submit = async () => {
  const formEl = DynamicsFormConstructorRef.value
  if (!formEl) return
  await formEl.validate().then(() => {
    emit('refresh', formEl?.getData(), currentIndex.value)
    isEdit.value = false
    currentItem.value = null as any
    currentIndex.value = null
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
