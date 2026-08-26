<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import type { FormInstance } from 'element-plus'

const props = defineProps<{
  // 表单字段数据
  modelValue: any
  // 可选的组件类型列表
  inputTypeList: Array<{ label: string; value: string }>
}>()
const emit = defineEmits(['update:modelValue'])

// 中转，规避 v-model 直接绑定 prop 成员；属性级修改会同步回父组件（同一对象引用）
const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// 批量注册构造器组件
const constructorModules = import.meta.glob('./items/*.vue', { eager: true })
const constructorComponents: Record<string, any> = {}
for (const [path, module] of Object.entries(constructorModules)) {
  const name = path.split('/').pop()?.replace('.vue', '') || ''
  constructorComponents[name] = (module as any).default
}

const currentConstructor = computed(
  () => constructorComponents[props.modelValue.input_type] || null,
)

const ruleFormRef = ref<FormInstance>()
const componentFormRef = ref<any>()

const rules = {
  label: [{ required: true, message: '显示名称 为必填属性' }],
  field: [{ required: true, message: '参数 为必填属性' }],
  required: [{ required: true, message: '是否必填 为必填属性' }],
  input_type: [{ required: true, message: '组建类型 为必填属性' }],
}

const validate = () => (ruleFormRef.value ? ruleFormRef.value.validate() : Promise.resolve())

const getData = () => {
  let label: string | any = form.value.label
  if (form.value.tooltip) {
    label = {
      input_type: 'TooltipLabel',
      label: form.value.label,
      attrs: { tooltip: form.value.tooltip },
      props_info: {},
    }
  }
  return {
    label,
    required: form.value.required,
    field: form.value.field,
    default_value: form.value.default_value,
    show_default_value: form.value.show_default_value,
    ...(componentFormRef.value?.getData() ?? {}),
  }
}

const rander = (data: any) => {
  form.value.required = data.required ? data.required : false
  form.value.field = data.field
  if (data.show_default_value !== undefined) {
    form.value.show_default_value = data.show_default_value
  }
  if (data.input_type) {
    form.value.input_type = data.input_type + 'Constructor'
  }
  if (data.label && data.label.input_type === 'TooltipLabel') {
    form.value.tooltip = data.label.attrs.tooltip
    form.value.label = data.label.label
  } else {
    form.value.label = data.label
  }
  nextTick(() => {
    componentFormRef.value?.rander(data)
  })
}

defineExpose({ validate, getData, rander })
</script>
<template>
  <el-form @submit.prevent ref="ruleFormRef" class="mb-24" label-width="auto" :model="form">
    <el-form-item label="参数" :required="true" prop="field" :rules="rules.field">
      <el-input v-model="form.field" :maxlength="64" placeholder="请输入参数" show-word-limit />
    </el-form-item>
    <el-form-item label="显示名称" :required="true" prop="label" :rules="rules.label">
      <el-input v-model="form.label" :maxlength="64" show-word-limit placeholder="请输入显示名称" />
    </el-form-item>
    <el-form-item label="参数提示说明">
      <el-input
        v-model="form.tooltip"
        :maxlength="128"
        show-word-limit
        placeholder="请输入参数提示说明"
      />
    </el-form-item>
    <el-form-item
      label="是否必填"
      :required="true"
      prop="required"
      :rules="rules.required"
      @click.prevent
    >
      <el-switch v-model="form.required" :active-value="true" :inactive-value="false" />
    </el-form-item>
    <el-form-item label="组件类型" :required="true" prop="input_type" :rules="rules.input_type">
      <el-select v-model="form.input_type" placeholder="请选择组件类型">
        <el-option
          v-for="item in inputTypeList"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </el-form-item>
    <component
      v-if="form.input_type && currentConstructor"
      ref="componentFormRef"
      :model-value="form"
      @update:model-value="(val: any) => Object.assign(form, val)"
      :is="currentConstructor"
    ></component>
  </el-form>
</template>
