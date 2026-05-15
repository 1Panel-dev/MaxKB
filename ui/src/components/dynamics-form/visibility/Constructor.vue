<template>
  <div>
    <el-radio-group v-model="formData.action" class="mb-8">
      <el-radio value="show">显示条件</el-radio>
      <el-radio value="hide">隐藏条件</el-radio>
    </el-radio-group>

    <div class="flex align-center mb-8">
      <span>符合以下</span>
      <el-select v-model="formData.condition" size="small" style="width: 60px; margin: 0 8px">
        <el-option label="所有" value="and" />
        <el-option label="任意" value="or" />
      </el-select>
      <span>条件</span>
    </div>

    <ConditionRow
      v-for="(cond, idx) in formData.conditions"
      :key="cond.id"
      :cond="cond"
      :index="idx"
      :nodeModel="nodeModel"
      :currentNodeFields="currentNodeFields"
      :currentEditingIndex="currentEditingIndex"
      @delete="removeCondition(idx)"
      class="mb-8"
    />

    <el-button link type="primary" @click="addCondition">
      <AppIcon iconName="app-add-outlined" class="mr-4" />
      添加
    </el-button>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { randomId } from '@/utils/common'
import type { CompareOptions, VisibilityRules } from './index'
import { inferFieldType, getAllowedOps, getFieldConfig } from './field-type'
import { compareList } from '@/workflow/common/data'
import ConditionRow from './ConditionRow.vue'

const props = defineProps<{
  initialValue?: VisibilityRules | null
  nodeModel?: any
  currentNodeFields?: Array<any>
  currentEditingIndex?: number
}>()

const formData = ref({
  action: 'show' as 'show' | 'hide',
  condition: 'and' as 'and' | 'or',
  conditions: [] as Array<any>,
})

function addCondition() {
  formData.value.conditions.push({
    id: randomId(),
    field: ['', ''] as [string, string],
    compare: '',
    value: '',
  })
}

function removeCondition(idx: number) {
  formData.value.conditions.splice(idx, 1)
}

function validate(): Promise<void> {
  for (const cond of formData.value.conditions) {
    const hasAny = cond.field[0] || cond.field[1] || cond.compare
    if (!hasAny) continue
    if (!cond.field[0] || !cond.field[1]) {
      return Promise.reject('请选择变量')
    }
    if (!cond.compare) {
      return Promise.reject('请选择运算符')
    }
    if (!['is_true', 'is_not_true'].includes(cond.compare) && !cond.value && cond.value !== 0) {
      return Promise.reject('请填写匹配值')
    }
  }
  return Promise.resolve()
}

function getData(): VisibilityRules | null {
  const conds = formData.value.conditions

  if (conds.length === 0) return null
  return {
    action: formData.value.action,
    condition: formData.value.condition,
    node_id: props.nodeModel?.id,
    conditions: conds.map((c) => ({
      id: c.id,
      field: c.field,
      compare: c.compare,
      value: c.value,
      // _ops, _fieldType, _options 不持久化
    })),
  }
}

function restore(rules: VisibilityRules | null) {
  if (rules && rules.conditions?.length) {
    formData.value.action = rules.action
    formData.value.condition = rules.condition
    formData.value.conditions = rules.conditions.map((c) => ({
      id: c.id || randomId(),
      field: [c.field[0], c.field[1]],
      compare: c.compare,
      value: c.value,
    }))
    formData.value.conditions.forEach((cond) => {
      if (cond.field && cond.field[0] && cond.field[1]) {
        const fieldType = inferFieldType(cond.field, props.nodeModel, props.currentNodeFields)
        const allowed = getAllowedOps(fieldType)
        const fieldConfig = getFieldConfig(cond.field, props.nodeModel, props.currentNodeFields)
        cond._ops = compareList.filter((op) => allowed.includes(op.value))
        cond._fieldType = fieldType
        cond._options = fieldConfig?.option_list ?? []
      }
    })
  }
}

onMounted(() => {
  formData.value.conditions = [
    {
      id: randomId(),
      field: ['', ''] as [string, string],
      compare: '',
      value: '',
    },
  ]
})

defineExpose({ getData, restore, validate })
</script>
<style lang="scss" scoped></style>
