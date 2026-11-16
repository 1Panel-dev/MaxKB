<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { compareList } from '@/workflow-canvas/config/constants'
import type { VisibilityConditionState, VisibilityFieldOption } from '../../type'
import FieldSelector from './FieldSelector.vue'
import { getAllowedOps, getFieldConfig, inferFieldType } from './utils'

const { t } = useI18n({ useScope: 'global' })

const condition = defineModel<VisibilityConditionState>({ required: true })

const props = defineProps<{ leftOptions?: VisibilityFieldOption[] }>()

function handleFieldChange() {
  condition.value._fieldError = ''
  condition.value._compareError = ''
  condition.value._valueError = ''

  const fieldType = inferFieldType(condition.value.field, props.leftOptions)
  const fieldConfig = getFieldConfig(condition.value.field, props.leftOptions)
  const isTreeMultiple = fieldType === 'TreeSelect' && fieldConfig?.attrs?.multiple
  const allowedOperations = isTreeMultiple ? ['contain', 'not_contain'] : getAllowedOps(fieldType)

  condition.value._ops = compareList.filter((operation) => allowedOperations.includes(operation.value))
  condition.value._fieldType = fieldType
  condition.value._options = fieldConfig?.option_list ?? []
  condition.value._treeData = fieldConfig?.attrs?.data ?? []
  condition.value._treeMultiple = isTreeMultiple

  const isMultiple = fieldType === 'MultiSelect' || isTreeMultiple
  if (!allowedOperations.includes(condition.value.compare)) {
    condition.value.compare = ''
    condition.value.value = isMultiple ? [] : ''
  }
}
</script>

<template>
  <el-form-item class="small min-w-0 flex-10" :error="condition._fieldError">
    <FieldSelector
      v-model="condition.field"
      :left-options="leftOptions"
      :placeholder="t('dynamicForm.defaultValue.variableRequired')"
      @change="handleFieldChange"
    />
  </el-form-item>

  <el-form-item class="small min-w-0 flex-6" :error="condition._compareError">
    <el-select v-model="condition.compare" clearable :placeholder="t('common.form.selectPlaceholder')" @change="condition._compareError = ''">
      <el-option
        v-for="operation in condition._ops || compareList"
        :key="operation.value"
        :label="t(operation.label)"
        :value="operation.value"
      />
    </el-select>
  </el-form-item>

  <el-form-item v-if="!['is_true', 'is_not_true'].includes(condition.compare)" class="small min-w-0 flex-6" :error="condition._valueError">
    <el-select
      v-if="['SingleSelect', 'RadioCard', 'RadioRow'].includes(condition._fieldType || '')"
      v-model="condition.value"
      clearable
      :placeholder="t('dynamicForm.options.valueRequired')"
      @change="condition._valueError = ''"
    >
      <el-option v-for="option in condition._options || []" :key="option.value" :label="`${option.label} (${option.value})`" :value="option.value" />
    </el-select>

    <el-select
      v-else-if="condition._fieldType === 'MultiSelect'"
      v-model="condition.value"
      clearable
      multiple
      :placeholder="t('dynamicForm.options.valueRequired')"
      @change="condition._valueError = ''"
    >
      <el-option v-for="option in condition._options || []" :key="option.value" :label="`${option.label} (${option.value})`" :value="option.value" />
    </el-select>

    <el-tree-select
      v-else-if="condition._fieldType === 'TreeSelect'"
      v-model="condition.value"
      :data="condition._treeData || []"
      :multiple="condition._treeMultiple"
      :render-after-expand="false"
      clearable
      :placeholder="t('dynamicForm.options.valueRequired')"
      @change="condition._valueError = ''"
    />

    <el-input v-else v-model="condition.value" :placeholder="t('dynamicForm.options.valueRequired')" @input="condition._valueError = ''" />
  </el-form-item>
</template>
