<template>
  <el-row :gutter="8">
    <el-col :span="8">
      <el-form-item :error="cond._fieldError">
        <FieldSelector
          :nodeModel="nodeModel"
          v-model="cond.field"
          @change="onFieldChange"
          :currentNodeFields="currentNodeFields"
          :currentEditingIndex="currentEditingIndex"
          class="w-full"
        />
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item :error="cond._compareError">
        <el-select v-model="cond.compare" @change="cond._compareError = ''" clearable>
          <el-option
            v-for="op in cond._ops || compareList"
            :key="op.value"
            :label="op.label"
            :value="op.value"
          />
        </el-select>
      </el-form-item>
    </el-col>
    <el-col :span="8" v-if="!['is_true', 'is_not_true'].includes(cond.compare)">
      <el-form-item :error="cond._valueError">
        <el-select
          v-if="['SingleSelect', 'RadioCard', 'RadioRow'].includes(cond._fieldType || '')"
          v-model="cond.value"
          @change="cond._valueError = ''"
          clearable
        >
          <el-option
            v-for="o in cond._options || []"
            :key="o.value"
            :label="`${o.label} (${o.value})`"
            :value="o.value"
          />
        </el-select>

        <el-select
          v-else-if="cond._fieldType === 'MultiSelect'"
          v-model="cond.value"
          @change="cond._valueError = ''"
          multiple
          clearable
        >
          <el-option
            v-for="o in cond._options || []"
            :key="o.value"
            :label="`${o.label} (${o.value})`"
            :value="o.value"
          />
        </el-select>

        <el-tree-select
          v-else-if="cond._fieldType === 'TreeSelect'"
          v-model="cond.value"
          @change="cond._valueError = ''"
          :data="cond._treeData || []"
          :multiple="cond._treeMultiple"
          :render-after-expand="false"
          clearable
        />

        <el-input v-else v-model="cond.value" @input="cond._valueError = ''" />
      </el-form-item>
    </el-col>
    <el-col :span="2">
      <el-button link type="info" @click="$emit('delete')">
        <AppIcon iconName="app-delete" />
      </el-button>
    </el-col>
  </el-row>
</template>
<script setup lang="ts">
import { compareList } from '@/workflow/common/data'
import FieldSelector from './FieldSelector.vue'
import { inferFieldType, getAllowedOps, getFieldConfig } from './field-type'
import type { CompareOptions } from './'

const props = defineProps<{
  cond: any
  index: number
  nodeModel: any
  currentNodeFields?: Array<any>
  currentEditingIndex?: number
}>()

defineEmits<{
  (e: 'delete'): void
}>()

function onFieldChange() {
  props.cond._fieldError = ''
  props.cond._compareError = ''
  props.cond._valueError = ''

  const fieldType = inferFieldType(props.cond.field, props.nodeModel, props.currentNodeFields)
  const fieldConfig = getFieldConfig(props.cond.field, props.nodeModel, props.currentNodeFields)

  const isTreeMultiple = fieldType === 'TreeSelect' && fieldConfig?.attrs?.multiple
  const allowed = isTreeMultiple ? ['contain', 'not_contain'] : getAllowedOps(fieldType)

  props.cond._ops = compareList.filter((op) => allowed.includes(op.value))
  props.cond._fieldType = fieldType
  props.cond._options = fieldConfig?.option_list ?? []
  props.cond._treeData = fieldConfig?.attrs?.data ?? []
  props.cond._treeMultiple = isTreeMultiple

  // 类型切换时重置 value
  const isMultiple = ['MultiSelect'].includes(fieldType || '') || isTreeMultiple

  if (!allowed.includes(props.cond.compare)) {
    props.cond.compare = ''
    props.cond.value = isMultiple ? [] : ''
  }
}
</script>
<style lang="scss" scoped></style>
