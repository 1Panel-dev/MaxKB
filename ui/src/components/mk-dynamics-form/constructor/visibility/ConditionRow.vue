<script setup lang="ts">
import { compareList } from '@/workflow-canvas/config/constants'
import FieldSelector from './FieldSelector.vue'
import { inferFieldType, getAllowedOps, getFieldConfig } from './index'
import type { LeftOptions } from '../type'

const condition = defineModel<MkDynamicFormValue>({ required: true })

const props = defineProps<{
  leftOptions?: Array<LeftOptions>
}>()

defineEmits<{
  (e: 'delete'): void
}>()

function onFieldChange() {
  condition.value._fieldError = ''
  condition.value._compareError = ''
  condition.value._valueError = ''

  const fieldType = inferFieldType(condition.value.field, props.leftOptions)
  const fieldConfig = getFieldConfig(condition.value.field, props.leftOptions)

  const isTreeMultiple = fieldType === 'TreeSelect' && fieldConfig?.attrs?.multiple
  const allowed = isTreeMultiple ? ['contain', 'not_contain'] : getAllowedOps(fieldType)

  condition.value._ops = compareList.filter((op) => allowed.includes(op.value))
  condition.value._fieldType = fieldType
  condition.value._options = fieldConfig?.option_list ?? []
  condition.value._treeData = fieldConfig?.attrs?.data ?? []
  condition.value._treeMultiple = isTreeMultiple

  // 类型切换时重置 value
  const isMultiple = ['MultiSelect'].includes(fieldType || '') || isTreeMultiple

  if (!allowed.includes(condition.value.compare)) {
    condition.value.compare = ''
    condition.value.value = isMultiple ? [] : ''
  }
}
</script>

<template>
  <el-row :gutter="8" class="w-full">
    <el-col :span="10">
      <el-form-item :error="condition._fieldError">
        <FieldSelector
          v-model="condition.field"
          @change="onFieldChange"
          :left-options="leftOptions"
          class="w-full"
          placeholder="请选择变量"
        />
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item :error="condition._compareError">
        <el-select
          v-model="condition.compare"
          @change="condition._compareError = ''"
          clearable
          placeholder="请选择比较方式"
        >
          <el-option
            v-for="op in condition._ops || compareList"
            :key="op.value"
            :label="op.label"
            :value="op.value"
          />
        </el-select>
      </el-form-item>
    </el-col>
    <el-col :span="6" v-if="!['is_true', 'is_not_true'].includes(condition.compare)">
      <el-form-item :error="condition._valueError">
        <el-select
          v-if="['SingleSelect', 'RadioCard', 'RadioRow'].includes(condition._fieldType || '')"
          v-model="condition.value"
          @change="condition._valueError = ''"
          clearable
          placeholder="请输入比较值"
        >
          <el-option
            v-for="o in condition._options || []"
            :key="o.value"
            :label="`${o.label} (${o.value})`"
            :value="o.value"
          />
        </el-select>

        <el-select
          v-else-if="condition._fieldType === 'MultiSelect'"
          v-model="condition.value"
          @change="condition._valueError = ''"
          multiple
          clearable
          placeholder="请输入比较值"
        >
          <el-option
            v-for="o in condition._options || []"
            :key="o.value"
            :label="`${o.label} (${o.value})`"
            :value="o.value"
          />
        </el-select>

        <el-tree-select
          v-else-if="condition._fieldType === 'TreeSelect'"
          v-model="condition.value"
          @change="condition._valueError = ''"
          :data="condition._treeData || []"
          :multiple="condition._treeMultiple"
          :render-after-expand="false"
          clearable
          placeholder="请输入比较值"
        />

        <el-input
          v-else
          v-model="condition.value"
          @input="condition._valueError = ''"
          placeholder="请输入比较值"
        />
      </el-form-item>
    </el-col>
    <el-col :span="1">
      <el-button link type="info" @click="$emit('delete')" class="mt-4">
        <MkIcon name="icon_delete-trash_outlined" />
      </el-button>
    </el-col>
  </el-row>
</template>
