<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue'
import { dynamicFormTypeOptions } from '@/components/mk-dynamics-form/constant'
import VisibilityConstructor from './visibility/index.vue'
import BasicInfoConstructor from './BasicInfoConstructor.vue'
import type { DynamicFormConstructorExpose, DynamicFormConstructorOption, DynamicFormConstructorState, FormField, VisibilityFieldOption, VisibilityRules } from '../type'

interface VisibilityConstructorExpose {
  getData: () => VisibilityRules | null
  render: (rules: VisibilityRules | null) => void
  validate: () => Promise<void>
}

// $attrs（label-position 等）显式透传给 BasicInfoConstructor 的 el-form
defineOptions({ name: 'MkDynamicsFormConstructor', inheritAttrs: false })
// 声明 v-model 事件，避免其监听器漏入 $attrs 透传到子表单
defineEmits<{ (event: 'update:modelValue', value: Partial<FormField>): void }>()

const props = withDefaults(
  defineProps<{ modelValue?: Partial<FormField>; fieldTypeOptions?: DynamicFormConstructorOption[]; enableVisibility?: boolean; leftOptions?: VisibilityFieldOption[] }>(),
  { enableVisibility: false, fieldTypeOptions: () => dynamicFormTypeOptions.map((item) => ({ label: item.label, value: `${item.value}Constructor` })) },
)

const activeTab = ref('basic')
const basicRef = ref<DynamicFormConstructorExpose>()
const visibilityRef = ref<VisibilityConstructorExpose>()
const visibilityRules = ref<VisibilityRules | null>(null)

const formData = ref<DynamicFormConstructorState>({ label: '', field: '', tooltip: '', required: false, input_type: '' })

const getData = (): FormField => {
  const fieldData = basicRef.value?.getData() ?? {}
  return {
    ...fieldData,
    field: fieldData.field ?? formData.value.field,
    input_type: fieldData.input_type ?? formData.value.input_type.replace(/Constructor$/, ''),
    visibility_rules: visibilityRef.value?.getData() ?? null,
  }
}

const validate = () => {
  const promises: Promise<unknown>[] = []
  if (basicRef.value?.validate) {
    promises.push(basicRef.value.validate())
  }
  if (visibilityRef.value?.validate) {
    promises.push(visibilityRef.value.validate())
  }
  return Promise.all(promises)
}

onMounted(() => {
  if (props.modelValue) {
    render(props.modelValue)
  }
})

const render = (data: Partial<FormField>) => {
  const fieldData: FormField = { ...data, field: data.field ?? '', input_type: data.input_type ?? '' }
  visibilityRules.value = fieldData.visibility_rules ?? null
  nextTick(() => {
    basicRef.value?.render(fieldData)
    visibilityRef.value?.render(fieldData.visibility_rules ?? null)
  })
}

defineExpose({ getData, validate, render })
</script>

<template>
  <el-tabs v-if="enableVisibility" v-model="activeTab">
    <el-tab-pane label="基本信息" name="basic">
      <BasicInfoConstructor ref="basicRef" v-model="formData" :input-type-list="fieldTypeOptions" v-bind="$attrs" />
    </el-tab-pane>
    <el-tab-pane label="显隐设置" name="visibility">
      <VisibilityConstructor ref="visibilityRef" :initial-value="visibilityRules" :left-options="leftOptions" />
    </el-tab-pane>
  </el-tabs>

  <BasicInfoConstructor v-else ref="basicRef" v-model="formData" :input-type-list="fieldTypeOptions" v-bind="$attrs" />
</template>
