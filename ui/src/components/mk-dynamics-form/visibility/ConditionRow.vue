<template>
  <el-row :gutter="8" class="w-full">
    <el-col :span="10">
      <el-form-item :error="cond._fieldError">
        <FieldSelector
          v-model="cond.field"
          @change="onFieldChange"
          :leftOptions="leftOptions"
          class="w-full"
          placeholder="请选择变量"
        />
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item :error="cond._compareError">
        <el-select
          v-model="cond.compare"
          @change="cond._compareError = ''"
          clearable
          placeholder="请选择比较方式"
        >
          <el-option
            v-for="op in cond._ops || compareList"
            :key="op.value"
            :label="op.label"
            :value="op.value"
          />
        </el-select>
      </el-form-item>
    </el-col>
    <el-col :span="6" v-if="!['is_true', 'is_not_true'].includes(cond.compare)">
      <el-form-item :error="cond._valueError">
        <el-select
          v-if="['SingleSelect', 'RadioCard', 'RadioRow'].includes(cond._fieldType || '')"
          v-model="cond.value"
          @change="cond._valueError = ''"
          clearable
          placeholder="请输入比较值"
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
          placeholder="请输入比较值"
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
          placeholder="请输入比较值"
        />

        <el-input
          v-else
          v-model="cond.value"
          @input="cond._valueError = ''"
          placeholder="请输入比较值"
        />
      </el-form-item>
    </el-col>
    <el-col :span="1">
      <el-button link type="info" @click="$emit('delete')" class="mt-4">
        <AppIcon iconName="app-delete" />
      </el-button>
    </el-col>
  </el-row>
</template>
<script setup lang="ts">
import { compareList } from '@/workflow-canvas/config/constants'
import FieldSelector from './FieldSelector.vue'
import { inferFieldType, getAllowedOps, getFieldConfig } from './field-type'
import type { LeftOptions } from '../constructor/type'

const props = defineProps<{
  cond: any
  index: number
  leftOptions?: Array<LeftOptions>
}>()

defineEmits<{
  (e: 'delete'): void
}>()

function onFieldChange() {
  props.cond._fieldError = ''
  props.cond._compareError = ''
  props.cond._valueError = ''

  const fieldType = inferFieldType(props.cond.field, props.leftOptions)
  const fieldConfig = getFieldConfig(props.cond.field, props.leftOptions)

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
