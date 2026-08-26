<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
import { computed, onMounted, ref, inject } from 'vue'
import VariableCascader from '../VariableCascader.vue'
import JsonInput from '@/components/mk-dynamics-form/items/JsonInput.vue'
const props = defineProps<{
  modelValue: MkDynamicFormValue
}>()
const getModel = inject('getModel') as MkDynamicFormValue

const assignment_method_option_list = computed(() => {
  const option_list = [
    {
      label: '自定义',
      value: 'custom',
    },
  ]
  if (getModel) {
    option_list.push({
      label: '引用变量',
      value: 'ref_variables',
    })
  }
  return option_list
})

const model = computed(() => {
  if (getModel) {
    return getModel()
  } else {
    return null
  }
})
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})
const jsonInputRef = ref<InstanceType<typeof JsonInput>>()
const getData = () => {
  return {
    input_type: 'JsonInput',
    attrs: {},
    props_info: {
      rules: [
        {
          required: formValue.value.required,
          validator: `validator = (rule, value, callback) => {
            return componentFormRef.value?.validate_rules(rule, value, callback);

}`,
          trigger: 'blur',
        },
      ],
    },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    default_value_assignment_method: formValue.value.default_value_assignment_method || 'custom',
  }
}

const default_value_rule = {
  required: true,
  validator: (
    rule: MkDynamicFormValue,
    value: MkDynamicFormValue,
    callback: MkDynamicFormValue,
  ) => {
    jsonInputRef.value?.validate_rules(rule, value, callback)
    return true
  },
  trigger: 'blur',
}
const default_ref_variables_value_rule = {
  required: true,
  validator: (
    rule: MkDynamicFormValue,
    value: MkDynamicFormValue,
    callback: MkDynamicFormValue,
  ) => {
    if (!(Array.isArray(value) && value.length > 1)) {
      callback('引用变量必填')
    }

    return true
  },
  trigger: 'blur',
}

const render = (form_data: MkDynamicFormValue) => {
  formValue.value.default_value = form_data.default_value
  formValue.value.default_value_assignment_method =
    form_data.default_value_assignment_method || 'custom'
}
defineExpose({ getData, render })
onMounted(() => {
  formValue.value.default_value = {}
  formValue.value.default_value_assignment_method = 'custom'
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>

<template>
  <el-form-item v-if="getModel">
    <template #label>
      <div class="flex-between">赋值方式</div>
    </template>

    <el-row class="w-full">
      <el-radio-group v-model="formValue.default_value_assignment_method">
        <el-radio
          :value="item.value"
          size="large"
          v-for="(item, index) in assignment_method_option_list"
          :key="index"
        >
          <span class="flex align-center">
            {{ item.label }}

            <el-tooltip effect="dark" placement="right" v-if="item.value === 'ref_variables'">
              <template #content> 变量的值必须符合: JSON 格式 </template>
              <MkIcon name="icon_warning_filled" class="app-warning-icon ml-4"></MkIcon>
            </el-tooltip>
          </span>
        </el-radio>
      </el-radio-group>
    </el-row>
  </el-form-item>
  <el-form-item
    v-if="formValue.default_value_assignment_method === 'ref_variables'"
    :required="true"
    prop="default_value"
    :rules="[default_ref_variables_value_rule]"
  >
    <VariableCascader
      ref="nodeCascaderRef"
      :variable-source="model"
      class="w-full"
      placeholder="请选择变量"
      v-model="formValue.default_value"
    />
  </el-form-item>

  <el-form-item
    class="defaultValueItem"
    label="默认值"
    :required="formValue.required"
    v-if="formValue.default_value_assignment_method === 'custom'"
    prop="default_value"
    :rules="[default_value_rule]"
  >
    <div class="defaultValueCheckbox">
      <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
    </div>
    <JsonInput ref="jsonInputRef" v-model="formValue.default_value"> </JsonInput>
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
