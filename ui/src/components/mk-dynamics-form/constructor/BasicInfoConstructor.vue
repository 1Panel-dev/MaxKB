<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import type { Component } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { DynamicFormConstructorExpose, DynamicFormConstructorOption, DynamicFormConstructorState, FormField, FormFieldLabel } from '../type'

interface ConstructorModule {
  default: Component
}

const props = defineProps<{ modelValue: DynamicFormConstructorState; inputTypeList: DynamicFormConstructorOption[] }>()
const emit = defineEmits<{ (event: 'update:modelValue', value: DynamicFormConstructorState): void }>()

// 中转，规避 v-model 直接绑定 prop 成员；属性级修改会同步回父组件（同一对象引用）
const form = computed({ get: () => props.modelValue, set: (value) => emit('update:modelValue', value) })

// 批量注册构造器组件
const constructorModules = import.meta.glob('./items/*.vue', { eager: true })
const constructorComponents: Record<string, Component> = {}
for (const [path, module] of Object.entries(constructorModules)) {
  const name = path.split('/').pop()?.replace('.vue', '') || ''
  constructorComponents[name] = (module as ConstructorModule).default
}

const currentConstructor = computed(() => constructorComponents[props.modelValue.input_type] || null)

const ruleFormRef = ref<FormInstance>()
const componentFormRef = ref<DynamicFormConstructorExpose>()

const rules: FormRules<DynamicFormConstructorState> = {
  label: [{ required: true, message: '请输入显示名称' }],
  field: [{ required: true, message: '请输入参数' }],
  input_type: [{ required: true, message: '请选择组件类型' }],
}

const validate = () => (ruleFormRef.value ? ruleFormRef.value.validate() : Promise.resolve())

const getData = (): FormField => {
  let label: string | FormFieldLabel = form.value.label
  if (form.value.tooltip) {
    label = { input_type: 'TooltipLabel', label: form.value.label, attrs: { tooltip: form.value.tooltip }, props_info: {} }
  }
  const componentData = componentFormRef.value?.getData() ?? {}
  return {
    ...componentData,
    label,
    required: form.value.required,
    field: form.value.field,
    input_type: componentData.input_type ?? form.value.input_type.replace(/Constructor$/, ''),
    default_value: form.value.default_value,
    show_default_value: form.value.show_default_value,
  }
}

const render = (data: FormField) => {
  form.value.required = data.required ?? false
  form.value.field = data.field
  if (data.show_default_value !== undefined) {
    form.value.show_default_value = data.show_default_value
  }
  if (data.input_type) {
    form.value.input_type = data.input_type + 'Constructor'
  }
  if (typeof data.label === 'object' && data.label?.input_type === 'TooltipLabel') {
    form.value.tooltip = String(data.label.attrs?.tooltip ?? '')
    form.value.label = data.label.label ?? ''
  } else {
    form.value.tooltip = ''
    form.value.label = typeof data.label === 'string' ? data.label : (data.label?.label ?? '')
  }
  nextTick(() => {
    componentFormRef.value?.render(data)
  })
}

const updateForm = (value: DynamicFormConstructorState) => {
  Object.assign(form.value, value)
}

defineExpose({ validate, getData, render })
</script>
<template>
  <el-form @submit.prevent ref="ruleFormRef" label-position="top" require-asterisk-position="right" :model="form">
    <el-form-item label="参数" prop="field" :rules="rules.field">
      <el-input v-model="form.field" :maxlength="64" placeholder="请输入参数" show-word-limit />
    </el-form-item>
    <el-form-item label="显示名称" prop="label" :rules="rules.label">
      <el-input v-model="form.label" :maxlength="64" show-word-limit placeholder="请输入显示名称" />
    </el-form-item>
    <el-form-item label="参数提示说明">
      <el-input v-model="form.tooltip" :maxlength="128" show-word-limit placeholder="请输入参数提示说明" />
    </el-form-item>
    <el-form-item label="是否必填" prop="required" @click.prevent>
      <el-switch v-model="form.required" :active-value="true" :inactive-value="false" />
    </el-form-item>
    <el-form-item label="组件类型" prop="input_type" :rules="rules.input_type">
      <el-select v-model="form.input_type" placeholder="请选择组件类型">
        <el-option v-for="item in inputTypeList" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
    </el-form-item>
    <component v-if="form.input_type && currentConstructor" ref="componentFormRef" :model-value="form" @update:model-value="updateForm" :is="currentConstructor"></component>
  </el-form>
</template>
