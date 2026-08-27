<script setup lang="ts">
import { compareList } from '@/workflow-canvas/config/constants'
import type { VisibilityConditionState, VisibilityFieldOption } from '../../type'
import FieldSelector from './FieldSelector.vue'
import { getAllowedOps, getFieldConfig, inferFieldType } from './utils'

const condition = defineModel<VisibilityConditionState>({ required: true })

const props = defineProps<{
  leftOptions?: VisibilityFieldOption[]
}>()

function handleFieldChange() {
  condition.value._fieldError = ''
  condition.value._compareError = ''
  condition.value._valueError = ''

  const fieldType = inferFieldType(condition.value.field, props.leftOptions)
  const fieldConfig = getFieldConfig(condition.value.field, props.leftOptions)
  const isTreeMultiple = fieldType === 'TreeSelect' && fieldConfig?.attrs?.multiple
  const allowedOperations = isTreeMultiple ? ['contain', 'not_contain'] : getAllowedOps(fieldType)

  condition.value._ops = compareList.filter((operation) =>
    allowedOperations.includes(operation.value),
  )
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
  <el-form-item class="min-w-0 flex-[10_1_0%]" :error="condition._fieldError">
    <FieldSelector
      v-model="condition.field"
      :left-options="leftOptions"
      class="w-full"
      placeholder="请选择变量"
      @change="handleFieldChange"
    />
  </el-form-item>

  <el-form-item class="min-w-0 flex-[6_1_0%]" :error="condition._compareError">
    <el-select
      v-model="condition.compare"
      clearable
      placeholder="请选择比较方式"
      @change="condition._compareError = ''"
    >
      <el-option
        v-for="operation in condition._ops || compareList"
        :key="operation.value"
        :label="operation.label"
        :value="operation.value"
      />
    </el-select>
  </el-form-item>

  <el-form-item
    v-if="!['is_true', 'is_not_true'].includes(condition.compare)"
    class="min-w-0 flex-[6_1_0%]"
    :error="condition._valueError"
  >
    <el-select
      v-if="['SingleSelect', 'RadioCard', 'RadioRow'].includes(condition._fieldType || '')"
      v-model="condition.value"
      clearable
      placeholder="请输入比较值"
      @change="condition._valueError = ''"
    >
      <el-option
        v-for="option in condition._options || []"
        :key="option.value"
        :label="`${option.label} (${option.value})`"
        :value="option.value"
      />
    </el-select>

    <el-select
      v-else-if="condition._fieldType === 'MultiSelect'"
      v-model="condition.value"
      clearable
      multiple
      placeholder="请输入比较值"
      @change="condition._valueError = ''"
    >
      <el-option
        v-for="option in condition._options || []"
        :key="option.value"
        :label="`${option.label} (${option.value})`"
        :value="option.value"
      />
    </el-select>

    <el-tree-select
      v-else-if="condition._fieldType === 'TreeSelect'"
      v-model="condition.value"
      :data="condition._treeData || []"
      :multiple="condition._treeMultiple"
      :render-after-expand="false"
      clearable
      placeholder="请输入比较值"
      @change="condition._valueError = ''"
    />

    <el-input
      v-else
      v-model="condition.value"
      placeholder="请输入比较值"
      @input="condition._valueError = ''"
    />
  </el-form-item>
</template>
