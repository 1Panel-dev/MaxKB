<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { referenceOptionsHelp } from '../../constant'
import type { DynamicFormConstructorOption, DynamicFormValidatorCallback, DynamicFormValue } from '../../type'
import { computed, onMounted, inject } from 'vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'

const { t } = useI18n({ useScope: 'global' })
const getModel = inject<() => DynamicFormValue>('getModel')

const assignmentMethodOptions = computed(() => {
  const options = [{ label: t('common.options.custom'), value: 'custom' }]
  if (getModel) {
    options.push({ label: t('dynamicForm.defaultValue.reference'), value: 'ref_variables' })
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
      callback(t('dynamicForm.defaultValue.referenceInputRequired'))
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
  if (option.value && formValue.value.default_value === option.value) {
    formValue.value.default_value = ''
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
    input_type: 'SingleSelect',
    attrs: {},
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    text_field: 'label',
    value_field: 'value',
    option_list: formValue.value.assignment_method === 'ref_variables' ? formValue.value.option_list : completeOptions.value,
    assignment_method: formValue.value.assignment_method || 'custom',
  }
}
const render = (formData: DynamicFormValue) => {
  formValue.value.option_list = formData.option_list || []
  formValue.value.default_value = formData.default_value
  formValue.value.show_default_value = formData.show_default_value
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
  <el-form-item v-if="getModel" :label="t('dynamicForm.defaultValue.assignmentMethod')">
    <el-radio-group @change="resetOptions" v-model="formValue.assignment_method">
      <el-radio :value="item.value" v-for="(item, index) in assignmentMethodOptions" :key="index">
        <span class="flex-align-center gap-1">
          {{ item.label }}

          <MkTooltip placement="right" v-if="item.value === 'ref_variables'">
            <template #content>
              <div class="whitespace-pre-wrap">{{ t(referenceOptionsHelp) }}</div>
            </template>
            <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
          </MkTooltip>
        </span>
      </el-radio>
    </el-radio-group>
  </el-form-item>
  <el-form-item v-if="formValue.assignment_method === 'ref_variables'" :required="true" prop="option_list" :rules="[referenceVariableRule]">
    <NodeCascader
      ref="nodeCascaderRef"
      :nodeModel="model"
      :placeholder="t('dynamicForm.defaultValue.variableRequired')"
      v-model="formValue.option_list"
    />
  </el-form-item>
  <div v-if="formValue.assignment_method === 'custom'" class="mb-4">
    <div class="flex-between mb-2">
      <span>{{ t('dynamicForm.options.value') }}</span>
      <el-button text type="primary" @click.stop="addOption()">
        <MkIcon name="icon_add_outlined"></MkIcon>
      </el-button>
    </div>

    <div class="w-full mk-gray-card">
      <MkFormList v-model="formValue.option_list" :default-item="{ label: '', value: '' }" :show-add-button="false" @remove="handleOptionRemove">
        <template #default="{ index, item: option }">
          <el-form-item
            :label="index === 0 ? t('dynamicForm.options.label') : ''"
            :prop="`option_list.${index}.label`"
            :rules="[
              { whitespace: true, required: formValue.required, message: t('dynamicForm.options.labelRequired'), trigger: ['blur', 'change'] },
            ]"
            class="flex-1 small"
          >
            <el-input v-model="option.label" :placeholder="t('dynamicForm.options.labelRequired')" />
          </el-form-item>
          <el-form-item
            :label="index === 0 ? t('dynamicForm.options.value') : ''"
            :prop="`option_list.${index}.value`"
            :rules="[
              { whitespace: true, required: formValue.required, message: t('dynamicForm.options.valueRequired'), trigger: ['blur', 'change'] },
            ]"
            class="flex-1 small"
          >
            <el-input v-model="option.value" :placeholder="t('dynamicForm.options.valueRequired')" />
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
    :rules="formValue.required ? [{ required: true, message: t('common.form.inputField', { fieldName: t('dynamicForm.fields.defaultValue') }) }] : []"
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">{{ t('dynamicForm.fields.defaultValue') }}</span>
        <el-checkbox v-model="formValue.show_default_value" :label="t('dynamicForm.defaultValue.show')" />
      </div>
    </template>
    <el-select v-model="formValue.default_value">
      <el-option v-for="(option, index) in completeOptions" :key="index" :label="option.label" :value="option.value" />
    </el-select>
  </el-form-item>
</template>
<style lang="scss" scoped></style>
