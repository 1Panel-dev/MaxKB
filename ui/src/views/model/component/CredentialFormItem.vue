<template>
  <el-form-item
    v-if="shouldShow(field)"
    :label="getLabel(field)"
    :prop="field.field"
    :required="field.required"
    :rules="getRules(field)"
  >
    <!-- TextInput -->
    <el-input
      v-if="field.input_type === 'TextInput'"
      v-model="modelValue[field.field]"
      v-bind="field.attrs || {}"
      :placeholder="field.attrs?.placeholder || '请输入'"
      @input="onChange"
    />

    <!-- PasswordInput -->
    <el-input
      v-else-if="field.input_type === 'PasswordInput'"
      v-model="modelValue[field.field]"
      type="password"
      show-password
      v-bind="field.attrs || {}"
      :placeholder="field.attrs?.placeholder || '请输入'"
      @input="onChange"
    />

    <!-- TextareaInput -->
    <el-input
      v-else-if="field.input_type === 'TextareaInput'"
      v-model="modelValue[field.field]"
      type="textarea"
      v-bind="field.attrs || {}"
      :placeholder="field.attrs?.placeholder || '请输入'"
      :rows="4"
      @input="onChange"
    />

    <!-- SingleSelect -->
    <el-select
      v-else-if="field.input_type === 'SingleSelect'"
      v-model="modelValue[field.field]"
      v-bind="field.attrs || {}"
      :placeholder="field.attrs?.placeholder || '请选择'"
      :filterable="field.attrs?.filterable"
      :allow-create="field.attrs?.allowCreate"
      @change="onChange"
      style="width: 100%"
    >
      <el-option
        v-for="opt in resolvedOptions"
        :key="opt[field.value_field || 'value']"
        :label="opt[field.text_field || 'label'] || opt.label || opt.name"
        :value="opt[field.value_field || 'value']"
      />
    </el-select>

    <!-- SwitchInput -->
    <el-switch
      v-else-if="field.input_type === 'SwitchInput'"
      v-model="modelValue[field.field]"
      @change="onChange"
    />

    <!-- Slider -->
    <el-slider
      v-else-if="field.input_type === 'Slider'"
      v-model="modelValue[field.field]"
      v-bind="field.attrs || {}"
      @change="onChange"
      style="width: 100%"
    />

    <!-- Radio -->
    <el-radio-group
      v-else-if="field.input_type === 'Radio' || field.input_type === 'RadioRow'"
      v-model="modelValue[field.field]"
      @change="onChange"
    >
      <el-radio
        v-for="opt in resolvedOptions"
        :key="opt[field.value_field || 'value']"
        :value="opt[field.value_field || 'value']"
      >
        {{ opt[field.text_field || 'label'] || opt.label || opt.name }}
      </el-radio>
    </el-radio-group>

    <!-- RadioCard -->
    <el-radio-group
      v-else-if="field.input_type === 'RadioCard'"
      v-model="modelValue[field.field]"
      @change="onChange"
    >
      <el-radio-button
        v-for="opt in resolvedOptions"
        :key="opt[field.value_field || 'value']"
        :value="opt[field.value_field || 'value']"
      >
        {{ opt[field.text_field || 'label'] || opt.label || opt.name }}
      </el-radio-button>
    </el-radio-group>

    <!-- RadioButton -->
    <el-radio-group
      v-else-if="field.input_type === 'RadioButton'"
      v-model="modelValue[field.field]"
      @change="onChange"
    >
      <el-radio-button
        v-for="opt in resolvedOptions"
        :key="opt[field.value_field || 'value']"
        :value="opt[field.value_field || 'value']"
      >
        {{ opt[field.text_field || 'label'] || opt.label || opt.name }}
      </el-radio-button>
    </el-radio-group>

    <!-- Default fallback: TextInput -->
    <el-input v-else v-model="modelValue[field.field]" @input="onChange" />
  </el-form-item>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { FormField } from '@/api/type/common'

const props = defineProps<{
  field: FormField
  modelValue: Record<string, any>
  formValue: Record<string, any>
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: any): void
  (e: 'change', field: string, val: any): void
}>()

const resolvedOptions = computed(() => {
  const f = props.field
  if (f.option_list && f.option_list.length > 0) return f.option_list
  return []
})

function getLabel(field: FormField): string {
  if (!field.label) return ''
  if (typeof field.label === 'string') return field.label
  if (field.label.label) return field.label.label
  return field.label.text || ''
}

function getRules(field: FormField) {
  const rules: any[] = []
  if (field.required) {
    rules.push({ required: true, message: `${getLabel(field)}不能为空`, trigger: 'blur' })
  }
  return rules
}

function shouldShow(field: FormField): boolean {
  if (!field.relation_show_field_dict) return true
  const dict = field.relation_show_field_dict
  for (const depField of Object.keys(dict)) {
    const allowedValues = dict[depField]
    const actualValue = String(props.formValue[depField] ?? '')
    if (allowedValues && Array.isArray(allowedValues)) {
      if (!allowedValues.includes(actualValue)) return false
    }
  }
  return true
}

function onChange() {
  emit('change', props.field.field, props.modelValue)
}
</script>
