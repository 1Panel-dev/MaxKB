<template>
  <el-form-item label="时间类型" required>
    <el-select @change="type_change" v-model="formValue.type" placeholder="请选择时间类型">
      <el-option
        v-for="input_type in type_list"
        :key="input_type.value"
        :label="input_type.label"
        :value="input_type.value"
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
        v-for="input_type in type_dict[formValue.type]"
        :key="input_type.value"
        :label="input_type.value"
        :value="input_type.value"
      />
    </el-select>
  </el-form-item>
  <el-form-item
    class="defaultValueItem"
    :required="formValue.required"
    prop="default_value"
    label="默认值"
    :rules="formValue.required ? [{ required: true, message: '默认值 为必填属性' }] : []"
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
<script setup lang="ts">
import { computed, onBeforeMount } from 'vue'
const type_list = [
  {
    label: '年',
    value: 'year'
  },
  {
    label: '月',
    value: 'month'
  },
  {
    label: '日期',
    value: 'date'
  },
  {
    label: '日期时间',
    value: 'datetime'
  }
]
const type_dict: any = {
  year: [{ value: 'YYYY' }],
  month: [{ value: 'YYYY-MM' }],
  date: [{ value: 'YYYY-MM-DD' }],
  datetime: [{ value: 'YYYY-MM-DD HH:mm:ss' }]
}
const type_change = () => {
  formValue.value.format = type_dict[formValue.value.type][0].value
  formValue.value.default_value = ''
}
const props = defineProps<{
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  }
})

const getData = () => {
  return {
    input_type: 'DatePicker',
    attrs: {
      type: formValue.value.type,
      format: formValue.value.format,
      'value-format': formValue.value.format
    },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value
  }
}
const rander = (form_data: any) => {
  formValue.value.type = form_data.attrs.type
  formValue.value.format = form_data.attrs?.format
  formValue.value.default_value = form_data.default_value || ''
}
defineExpose({ getData, rander })
onBeforeMount(() => {
  formValue.value.type = 'datetime'
  formValue.value.format = 'YYYY-MM-DD HH:mm:ss'
  formValue.value.default_value = ''
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>
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
