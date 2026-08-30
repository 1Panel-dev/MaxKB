<script setup lang="ts">
import { computed, onMounted, ref, inject } from 'vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import JsonInput from '@/components/mk-dynamics-form/items/JsonInput.vue'
import type { DynamicFormValidatorCallback, DynamicFormValue } from '../../type'
const props = defineProps<{ modelValue: DynamicFormValue }>()
const getModel = inject<() => DynamicFormValue>('getModel')

const assignmentMethodOptions = computed(() => {
  const options = [{ label: '自定义', value: 'custom' }]
  if (getModel) {
    options.push({ label: '引用变量', value: 'ref_variables' })
  }
  return options
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
            return componentFormRef.value?.validateRules(rule, value, callback);

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

const defaultValueRule = {
  required: true,
  validator: (rule: unknown, value: DynamicFormValue, callback: (error?: Error) => void) => {
    jsonInputRef.value?.validateRules(rule, value, callback)
    return true
  },
  trigger: 'blur',
}
const referenceVariableRule = {
  required: true,
  validator: (_rule: unknown, value: DynamicFormValue, callback: DynamicFormValidatorCallback) => {
    if (!(Array.isArray(value) && value.length > 1)) {
      callback('请输入引用变量')
    }

    return true
  },
  trigger: 'blur',
}

const render = (formData: DynamicFormValue) => {
  formValue.value.default_value = formData.default_value
  formValue.value.default_value_assignment_method = formData.default_value_assignment_method || 'custom'
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
  <el-form-item v-if="getModel" label="赋值方式">
    <!-- // TODO 赋值方式待调整 -->
    <el-radio-group v-model="formValue.default_value_assignment_method">
      <el-radio :value="item.value" v-for="(item, index) in assignmentMethodOptions" :key="index">
        <span class="flex align-center">
          {{ item.label }}

          <el-tooltip placement="right" v-if="item.value === 'ref_variables'">
            <template #content> 变量的值必须符合: JSON 格式 </template>
            <MkIcon name="icon_info_outlined"></MkIcon>
          </el-tooltip>
        </span>
      </el-radio>
    </el-radio-group>
  </el-form-item>
  <el-form-item v-if="formValue.default_value_assignment_method === 'ref_variables'" :required="true" prop="default_value" :rules="[referenceVariableRule]">
    <NodeCascader ref="nodeCascaderRef" :nodeModel="model" class="w-full" placeholder="请选择变量" v-model="formValue.option_list" />
  </el-form-item>

  <el-form-item
    class="mk-hide-asterisk"
    :required="formValue.required"
    v-if="formValue.default_value_assignment_method === 'custom'"
    prop="default_value"
    :rules="[defaultValueRule]"
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">默认值</span>
        <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
      </div>
    </template>
    <JsonInput ref="jsonInputRef" v-model="formValue.default_value"> </JsonInput>
  </el-form-item>
</template>

<style lang="scss" scoped></style>
