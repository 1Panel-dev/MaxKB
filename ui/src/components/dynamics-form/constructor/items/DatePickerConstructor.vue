<template>
  <el-form-item :label="$t('dynamicsForm.DatePicker.dataType.label')" required>
    <el-select
      @change="type_change"
      v-model="formValue.type"
      :placeholder="$t('dynamicsForm.DatePicker.dataType.placeholder')"
    >
      <el-option
        v-for="input_type in type_list"
        :key="input_type.value"
        :label="input_type.label"
        :value="input_type.value"
      />
    </el-select>
  </el-form-item>
  <el-form-item :label="$t('dynamicsForm.DatePicker.format.label')" required>
    <el-select
      v-model="formValue.format"
      filterable
      default-first-option
      allow-create
      :placeholder="$t('dynamicsForm.DatePicker.format.placeholder')"
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
    :label="$t('dynamicsForm.default.label')"
    :rules="
      formValue.required
        ? [
            {
              required: true,
              message: `${$t('dynamicsForm.default.label')}${$t('dynamicsForm.default.requiredMessage')}`,
            },
          ]
        : []
    "
  >
    <div class="defaultValueCheckbox">
      <el-checkbox
        v-model="formValue.show_default_value"
        :label="$t('dynamicsForm.default.show')"
      />
    </div>
    <el-date-picker
      v-model="formValue.default_value"
      :type="formValue.type"
      :placeholder="$t('dynamicsForm.DatePicker.placeholder')"
      :format="formValue.format"
      :value-format="formValue.format"
    />
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onBeforeMount } from 'vue'
import moment from 'moment'
import { t } from '@/locales'
const type_list = [
  {
    label: t('dynamicsForm.DatePicker.year'),
    value: 'year',
  },
  {
    label: t('dynamicsForm.DatePicker.month'),
    value: 'month',
  },
  {
    label: t('dynamicsForm.DatePicker.date'),
    value: 'date',
  },
  {
    label: t('dynamicsForm.DatePicker.datetime'),
    value: 'datetime',
  },
]
const type_dict: any = {
  year: [{ value: 'YYYY' }],
  month: [{ value: 'YYYY-MM' }],
  date: [{ value: 'YYYY-MM-DD' }],
  datetime: [{ value: 'YYYY-MM-DD HH:mm:ss' }],
}

const type_change = () => {
  formValue.value.format = type_dict[formValue.value.type][0].value
  formValue.value.default_value = moment().format(formValue.value.format)
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
const rander = (form_data: any) => {
  formValue.value.type = form_data.attrs.type
  formValue.value.format = form_data.attrs?.format
  formValue.value.default_value = form_data.default_value
}
defineExpose({ getData, rander })
onBeforeMount(() => {
  formValue.value.type = 'datetime'
  formValue.value.format = 'YYYY-MM-DD HH:mm:ss'
  formValue.value.default_value = moment().format(formValue.value.format)
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
