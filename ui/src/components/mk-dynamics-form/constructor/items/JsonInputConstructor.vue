<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DynamicFormValidatorCallback, DynamicFormValue } from '../../type'
import JsonInput from '@/components/mk-dynamics-form/items/JsonInput.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ modelValue: DynamicFormValue }>()
const getModel = inject<() => DynamicFormValue>('getModel')

const assignmentMethodOptions = computed(() => {
  const options = [{ label: t('common.options.custom'), value: 'custom' }]
  if (getModel) {
    options.push({ label: t('common.options.referenceVariable'), value: 'ref_variables' })
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

// 自定义 JSON 和引用路径分别保留编辑值，当前方式的值参与校验和保存。
type AssignmentMethod = 'custom' | 'ref_variables'
const defaultValueDrafts: Record<AssignmentMethod, DynamicFormValue> = { custom: {}, ref_variables: [] }
const assignmentMethod = computed<AssignmentMethod>({
  get: () => formValue.value.default_value_assignment_method || 'custom',
  set: (method) => {
    defaultValueDrafts[assignmentMethod.value] = formValue.value.default_value
    formValue.value.default_value_assignment_method = method
    formValue.value.default_value = defaultValueDrafts[method]
  },
})

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
    default_value_assignment_method: assignmentMethod.value,
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
function isReferencePath(value: unknown): value is string[] {
  return Array.isArray(value) && value.length >= 2 && value.every((part) => typeof part === 'string' && part.length > 0)
}

const referenceVariableRule = {
  required: true,
  validator: (_rule: unknown, value: DynamicFormValue, callback: DynamicFormValidatorCallback) => {
    callback(isReferencePath(value) ? undefined : t('dynamicForm.fields.reference.selectRequiredMessage'))
  },
  trigger: 'blur',
}

const render = (formData: DynamicFormValue) => {
  defaultValueDrafts.custom = {}
  defaultValueDrafts.ref_variables = []
  formValue.value.default_value_assignment_method = formData.default_value_assignment_method || 'custom'
  formValue.value.default_value = assignmentMethod.value === 'ref_variables' && !isReferencePath(formData.default_value) ? [] : formData.default_value
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
  <el-form-item v-if="getModel" :label="t('dynamicForm.fields.assignment.label')">
    <el-radio-group v-model="assignmentMethod">
      <el-radio :value="item.value" v-for="(item, index) in assignmentMethodOptions" :key="index">
        <span class="flex-align-center gap-1">
          {{ item.label }}

          <MkTooltip placement="right" v-if="item.value === 'ref_variables'">
            <template #content>{{ t('dynamicForm.help.jsonFormat') }}</template>
            <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
          </MkTooltip>
        </span>
      </el-radio>
    </el-radio-group>
  </el-form-item>
  <el-form-item v-if="assignmentMethod === 'ref_variables'" :required="true" prop="default_value" :rules="[referenceVariableRule]">
    <NodeCascader
      ref="nodeCascaderRef"
      :nodeModel="model"
      :placeholder="t('dynamicForm.fields.variable.placeholder')"
      v-model="formValue.default_value"
    />
  </el-form-item>

  <el-form-item
    class="mk-hide-asterisk"
    :required="formValue.required"
    v-if="assignmentMethod === 'custom'"
    prop="default_value"
    :rules="[defaultValueRule]"
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">{{ t('dynamicForm.fields.defaultValue.label') }}</span>
        <el-checkbox v-model="formValue.show_default_value" :label="t('dynamicForm.options.showDefault')" />
      </div>
    </template>
    <JsonInput ref="jsonInputRef" v-model="formValue.default_value"></JsonInput>
  </el-form-item>
</template>

<style lang="scss" scoped></style>
