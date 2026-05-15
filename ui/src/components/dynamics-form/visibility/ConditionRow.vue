<template>
  <el-row :gutter="8">
    <el-col :span="8">
      <FieldSelector
        :nodeModel="nodeModel"
        v-model="cond.field"
        @change="onFieldChange"
        :currentNodeFields="currentNodeFields"
        :currentEditingIndex="currentEditingIndex"
        class="w-full"
      />
    </el-col>
    <el-col :span="6">
      <el-select v-model="cond.compare" clearable>
        <el-option
          v-for="op in cond._ops || compareList"
          :key="op.value"
          :label="op.label"
          :value="op.value"
        />
      </el-select>
    </el-col>
    <el-col :span="8" v-if="!['is_true', 'is_not_true'].includes(cond.compare)">
      <el-select
        v-if="['SingleSelect', 'RadioCard', 'RadioRow'].includes(cond._fieldType || '')"
        v-model="cond.value"
        clearable
      >
        <el-option
          v-for="o in cond._options || []"
          :key="o.value"
          :label="`${o.label} (${o.value})`"
          :value="o.value"
        />
      </el-select>

      <el-input v-else v-model="cond.value" />
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
  const fieldType = inferFieldType(props.cond.field, props.nodeModel, props.currentNodeFields)
  const allowed = getAllowedOps(fieldType)
  const fieldConfig = getFieldConfig(props.cond.field, props.nodeModel, props.currentNodeFields)

  props.cond._ops = compareList.filter((op) => allowed.includes(op.value))
  props.cond._fieldType = fieldType
  props.cond._options = fieldConfig?.option_list ?? []

  if (!allowed.includes(props.cond.compare)) {
    props.cond.compare = ''
    props.cond.value = ''
  }
}
</script>
<style lang="scss" scoped></style>
