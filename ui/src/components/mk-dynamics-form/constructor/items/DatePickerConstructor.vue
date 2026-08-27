<script setup lang="ts">
import { computed, onBeforeMount } from 'vue'
import { dateFormat, datetimeFormat } from '@/utils/time'
import type { DynamicFormConstructorOption, DynamicFormValue } from '../../type'

type DatePickerType = 'year' | 'month' | 'date' | 'datetime'
type DateFormatOption = Pick<DynamicFormConstructorOption, 'value'>

const defaultDatePickerType: DatePickerType = 'datetime'

const dateTypeOptions: DynamicFormConstructorOption[] = [
  {
    label: '年',
    value: 'year',
  },
  {
    label: '月',
    value: 'month',
  },
  {
    label: '日期',
    value: 'date',
  },
  {
    label: '日期时间',
    value: 'datetime',
  },
]
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
const props = defineProps<{
  modelValue: DynamicFormValue
}>()
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
    attrs: {
      type: formValue.value.type,
      format: formValue.value.format,
      'value-format': formValue.value.format,
    },
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
    <el-form-item class="min-w-0 flex-1" label="时间类型" required>
      <el-select
        v-model="formValue.type"
        placeholder="请选择时间类型"
        @change="handleDateTypeChange"
      >
        <el-option
          v-for="inputTypeOption in dateTypeOptions"
          :key="inputTypeOption.value"
          :label="inputTypeOption.label"
          :value="inputTypeOption.value"
        />
      </el-select>
    </el-form-item>
    <el-form-item class="min-w-0 flex-1" label="格式" required>
      <el-select
        v-model="formValue.format"
        filterable
        default-first-option
        allow-create
        placeholder="请选择格式"
      >
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
    :rules="
      formValue.required
        ? [
            {
              required: true,
              message: '请输入默认值',
            },
          ]
        : []
    "
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">默认值</span>
        <el-checkbox v-model="defaultValueUnselected" label="未选中项" />
      </div>
    </template>
    <el-date-picker
      v-model="formValue.default_value"
      :type="formValue.type"
      placeholder="选择日期"
      :format="formValue.format"
      :value-format="formValue.format"
      class="w-full!"
    />
  </el-form-item>
</template>
<style lang="scss" scoped></style>
