<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, onBeforeMount } from 'vue'
import { dateFormat, datetimeFormat } from '@/utils/time'
import type { DynamicFormConstructorOption, DynamicFormValue } from '../../type'

const { t } = useI18n({ useScope: 'global' })

type DatePickerType = 'year' | 'month' | 'date' | 'datetime'
type DateFormatOption = Pick<DynamicFormConstructorOption, 'value'>

const defaultDatePickerType: DatePickerType = 'datetime'

const dateTypeOptions = computed<DynamicFormConstructorOption[]>(() => [
  { label: t('dynamicForm.date.year'), value: 'year' },
  { label: t('dynamicForm.date.month'), value: 'month' },
  { label: t('dynamicForm.types.date'), value: 'date' },
  { label: t('dynamicForm.date.datetime'), value: 'datetime' },
])
const dateFormatOptions: Record<DatePickerType, DateFormatOption[]> = {
  year: [{ value: 'YYYY' }],
  month: [{ value: 'YYYY-MM' }],
  date: [{ value: 'YYYY-MM-DD' }],
  datetime: [{ value: 'YYYY-MM-DD HH:mm:ss' }],
}

const getCurrentDateValue = (type: DatePickerType) => {
  const now = new Date()
  if (type === 'datetime') {
    return datetimeFormat(now) as string
  }

  const currentDate = dateFormat(now) as string
  if (type === 'year') return currentDate.slice(0, 4)
  if (type === 'month') return currentDate.slice(0, 7)
  return currentDate
}

const handleDateTypeChange = () => {
  const datePickerType = formValue.value.type as DatePickerType
  const defaultFormat = dateFormatOptions[datePickerType][0]?.value
  if (!defaultFormat) return

  formValue.value.format = defaultFormat
  formValue.value.default_value = getCurrentDateValue(datePickerType)
}
const props = defineProps<{ modelValue: DynamicFormValue }>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const defaultValueUnselected = computed({
  get: () => formValue.value.show_default_value === false,
  set: (value: boolean) => {
    formValue.value.show_default_value = !value
  },
})

const getData = () => {
  return {
    input_type: 'DatePicker',
    attrs: { type: formValue.value.type, format: formValue.value.format, 'value-format': formValue.value.format },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
  }
}
const render = (formData: DynamicFormValue) => {
  formValue.value.type = formData.attrs.type
  formValue.value.format = formData.attrs?.format
  formValue.value.default_value = formData.default_value
}
defineExpose({ getData, render })
onBeforeMount(() => {
  formValue.value.type = defaultDatePickerType
  formValue.value.format = 'YYYY-MM-DD HH:mm:ss'
  formValue.value.default_value = getCurrentDateValue(defaultDatePickerType)
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>

<template>
  <div class="flex gap-4">
    <el-form-item class="min-w-0 flex-1" :label="t('dynamicForm.date.type')" required>
      <el-select v-model="formValue.type" :placeholder="t('dynamicForm.date.typeRequired')" @change="handleDateTypeChange">
        <el-option
          v-for="inputTypeOption in dateTypeOptions"
          :key="inputTypeOption.value"
          :label="inputTypeOption.label"
          :value="inputTypeOption.value"
        />
      </el-select>
    </el-form-item>
    <el-form-item class="min-w-0 flex-1" :label="t('dynamicForm.date.format')" required>
      <el-select v-model="formValue.format" filterable default-first-option allow-create :placeholder="t('dynamicForm.date.formatRequired')">
        <el-option
          v-for="inputTypeOption in dateFormatOptions[formValue.type as DatePickerType]"
          :key="inputTypeOption.value"
          :label="inputTypeOption.value"
          :value="inputTypeOption.value"
        />
      </el-select>
    </el-form-item>
  </div>
  <el-form-item
    class="mk-hide-asterisk"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: t('common.form.inputField', { fieldName: t('dynamicForm.fields.defaultValue') }) }] : []"
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">{{ t('dynamicForm.fields.defaultValue') }}</span>
        <el-checkbox v-model="defaultValueUnselected" :label="t('dynamicForm.date.unselected')" />
      </div>
    </template>
    <el-date-picker
      v-model="formValue.default_value"
      :type="formValue.type"
      :placeholder="t('dynamicForm.date.selectDate')"
      :format="formValue.format"
      :value-format="formValue.format"
      class="w-full!"
    />
  </el-form-item>
</template>
<style lang="scss" scoped></style>
