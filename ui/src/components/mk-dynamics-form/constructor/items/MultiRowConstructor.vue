<script setup lang="ts">
import { referenceOptionsHelp } from '../../constant'
import { computed, onMounted, inject } from 'vue'
import MultiRow from '../../items/MultiRow.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { DynamicFormConstructorOption, DynamicFormValidatorCallback, DynamicFormValue, FormField } from '../../type'
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
const addOption = () => {
  formValue.value.option_list.push({ value: '', label: '' })
}

const resetOptions = () => {
  formValue.value.option_list = []
  if (formValue.value.assignment_method === 'custom') addOption()
}

const handleOptionRemove = (option: DynamicFormConstructorOption) => {
  if (Array.isArray(formValue.value.default_value)) {
    formValue.value.default_value = formValue.value.default_value.filter((value: DynamicFormValue) => value !== option.value)
  }
}

// 编辑中的空行保留在表单内，仅完整选项参与默认值选择和配置输出。
const completeOptions = computed<DynamicFormConstructorOption[]>(() => {
  if (formValue.value.assignment_method === 'ref_variables') return []
  return (formValue.value.option_list || []).filter(
    (option: DynamicFormConstructorOption) => String(option.label ?? '').trim() && String(option.value ?? '').trim(),
  )
})

const getData = () => {
  return {
    input_type: 'MultiRow',
    attrs: {},
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    text_field: 'label',
    value_field: 'value',
    option_list: formValue.value.assignment_method === 'ref_variables' ? formValue.value.option_list : completeOptions.value,
    assignment_method: formValue.value.assignment_method || 'custom',
  }
}
const formField = computed<FormField>(() => ({ field: 'default_value', ...getData() }))

const render = (formData: DynamicFormValue) => {
  formValue.value.option_list = formData.option_list || []
  formValue.value.default_value = formData.default_value
  formValue.value.assignment_method = formData.assignment_method || 'custom'
  // 空配置回填后仍保留一行，供用户填写首个选项。
  if (formValue.value.assignment_method === 'custom' && !formValue.value.option_list.length) addOption()
}

defineExpose({ getData, render })
onMounted(() => {
  formValue.value.option_list = []
  formValue.value.default_value = ''
  formValue.value.assignment_method = 'custom'
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
  addOption()
})
</script>

<template>
  <el-form-item v-if="getModel" label="赋值方式">
    <el-radio-group @change="resetOptions" v-model="formValue.assignment_method">
      <el-radio :value="item.value" v-for="(item, index) in assignmentMethodOptions" :key="index">
        <span class="flex items-center gap-1">
          {{ item.label }}

          <el-tooltip placement="right" v-if="item.value === 'ref_variables'">
            <template #content>
              <div class="whitespace-pre-wrap">{{ referenceOptionsHelp }}</div>
            </template>
            <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
          </el-tooltip>
        </span>
      </el-radio>
    </el-radio-group>
  </el-form-item>
  <el-form-item v-if="formValue.assignment_method === 'ref_variables'" :required="true" prop="option_list" :rules="[referenceVariableRule]">
    <NodeCascader ref="nodeCascaderRef" :nodeModel="model" placeholder="请选择变量" v-model="formValue.option_list" />
  </el-form-item>

  <div v-if="formValue.assignment_method === 'custom'" class="mb-4">
    <div class="flex-between mb-2">
      <span>选项值</span>
      <el-button text type="primary" @click.stop="addOption()">
        <MkIcon name="icon_add_outlined"></MkIcon>
      </el-button>
    </div>

    <div class="w-full mk-gray-card">
      <MkFormList v-model="formValue.option_list" :default-item="{ label: '', value: '' }" :show-add-button="false" @remove="handleOptionRemove">
        <template #default="{ index, item: option }">
          <el-form-item
            :label="index === 0 ? '标签' : ''"
            :prop="`option_list.${index}.label`"
            :rules="[{ required: formValue.required, message: '请输入标签', trigger: ['blur', 'change'] }]"
            class="flex-1 small"
          >
            <el-input v-model="option.label" placeholder="请输入标签" />
          </el-form-item>
          <el-form-item
            :label="index === 0 ? '选项值' : ''"
            :prop="`option_list.${index}.value`"
            :rules="[{ required: formValue.required, message: '请输入选项值', trigger: ['blur', 'change'] }]"
            class="flex-1 small"
          >
            <el-input v-model="option.value" placeholder="请输入选项值" />
          </el-form-item>
        </template>
      </MkFormList>
    </div>
  </div>
  <el-form-item
    class="mk-hide-asterisk"
    v-if="formValue.assignment_method === 'custom'"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: '请输入默认值' }] : []"
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">默认值</span>
        <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
      </div>
    </template>
    <MultiRow v-if="completeOptions.length" v-model="formValue.default_value" :form-field="formField" :other-params="{}" field="default_value" />
  </el-form-item>
</template>
