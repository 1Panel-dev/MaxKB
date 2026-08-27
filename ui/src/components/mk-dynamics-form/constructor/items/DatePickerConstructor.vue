<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, onBeforeMount } from 'vue'
const dateTypeOptions = [
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
const dateFormatOptions: DynamicFormValue = {
  year: [{ value: 'YYYY' }],
  month: [{ value: 'YYYY-MM' }],
  date: [{ value: 'YYYY-MM-DD' }],
  datetime: [{ value: 'YYYY-MM-DD HH:mm:ss' }],
}

const padDatePart = (value: number) => String(value).padStart(2, '0')
const formatCurrentDate = (format: string) => {
  const now = new Date()
  return format
    .replace('YYYY', String(now.getFullYear()))
    .replace('MM', padDatePart(now.getMonth() + 1))
    .replace('DD', padDatePart(now.getDate()))
    .replace('HH', padDatePart(now.getHours()))
    .replace('mm', padDatePart(now.getMinutes()))
    .replace('ss', padDatePart(now.getSeconds()))
}

const handleDateTypeChange = () => {
  formValue.value.format = dateFormatOptions[formValue.value.type][0].value
  formValue.value.default_value = formatCurrentDate(formValue.value.format)
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
  formValue.value.type = 'datetime'
  formValue.value.format = 'YYYY-MM-DD HH:mm:ss'
  formValue.value.default_value = formatCurrentDate(formValue.value.format)
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>

<template>
  <el-form-item label="时间类型" required>
    <el-select @change="handleDateTypeChange" v-model="formValue.type" placeholder="请选择时间类型">
      <el-option
        v-for="inputTypeOption in dateTypeOptions"
        :key="inputTypeOption.value"
        :label="inputTypeOption.label"
        :value="inputTypeOption.value"
      />
    </el-select>
  </el-form-item>
  <el-form-item label="格式" required>
    <el-select
      v-model="formValue.format"
      filterable
      default-first-option
      allow-create
      placeholder="请选择格式"
    >
      <el-option
        v-for="inputTypeOption in dateFormatOptions[formValue.type]"
        :key="inputTypeOption.value"
        :label="inputTypeOption.value"
        :value="inputTypeOption.value"
      />
    </el-select>
  </el-form-item>
  <el-form-item
    class="defaultValueItem"
    :required="formValue.required"
    prop="default_value"
    label="默认值"
    :rules="
      formValue.required
        ? [
            {
              required: true,
              message: '默认值为必填属性',
            },
          ]
        : []
    "
  >
    <div class="defaultValueCheckbox">
      <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
    </div>
    <el-date-picker
      v-model="formValue.default_value"
      :type="formValue.type"
      placeholder="选择日期"
      :format="formValue.format"
      :value-format="formValue.format"
    />
  </el-form-item>
</template>
<style lang="scss" scoped>
.defaultValueItem {
  position: relative;
  .defaultValueCheckbox {
    position: absolute;
    right: 0;
    top: -35px;
  }
}
</style>
