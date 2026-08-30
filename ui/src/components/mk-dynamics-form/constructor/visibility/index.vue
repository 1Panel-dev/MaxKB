<script setup lang="ts">
import { computed, ref } from 'vue'
import { randomId } from '@/utils/common'
import MkFormList from '@/components/mk-form-list/index.vue'
import type { VisibilityConditionState, VisibilityFieldOption, VisibilityRules } from '../../type'
import { inferFieldType, getAllowedOps, getFieldConfig } from './utils'
import { compareList } from '@/workflow-canvas/config/constants'
import ConditionRow from './ConditionRow.vue'

defineOptions({ name: 'MkDynamicsFormVisibilityConstructor' })

const props = defineProps<{ initialValue?: VisibilityRules | null; leftOptions?: VisibilityFieldOption[] }>()

const defaultCondition: VisibilityConditionState = { id: '', field: ['', ''], compare: '', value: '' }

const formData = ref({
  action: 'show' as 'show' | 'hide',
  condition: 'and' as 'and' | 'or',
  conditions: [{ ...defaultCondition, id: randomId(), field: ['', ''] }] as VisibilityConditionState[],
})

const conditionRows = computed<VisibilityConditionState[]>({
  get: () => formData.value.conditions,
  set: (conditions) => {
    formData.value.conditions = conditions.map((condition) => (condition.id ? condition : { ...condition, id: randomId(), field: [...condition.field] as [string, string] }))
  },
})

function validate(): Promise<void> {
  let hasError = false
  for (const cond of formData.value.conditions) {
    cond._fieldError = ''
    cond._compareError = ''
    cond._valueError = ''
  }
  for (const cond of formData.value.conditions) {
    const hasAny = cond.field[0] || cond.field[1] || cond.compare
    if (!hasAny) continue
    if (!cond.field[0] || !cond.field[1]) {
      cond._fieldError = '请选择变量'
      hasError = true
    }
    if (!cond.compare) {
      cond._compareError = '请选择比较方式'
      hasError = true
    }
    const isEmpty = Array.isArray(cond.value) ? cond.value.length === 0 : !cond.value && cond.value !== 0
    if (!['is_true', 'is_not_true'].includes(cond.compare) && isEmpty) {
      cond._valueError = '请输入比较值'
      hasError = true
    }
  }
  return hasError ? Promise.reject() : Promise.resolve()
}

function getData(): VisibilityRules | null {
  const conds = formData.value.conditions

  if (conds.length === 0) return null
  const selfScope = (props.leftOptions ?? []).find((item) => item.self)
  return {
    action: formData.value.action,
    condition: formData.value.condition,
    conditions: conds
      .filter((c) => c.field[0] && c.field[1] && c.compare)
      .map((c) => ({
        id: c.id,
        field: c.field,
        self: c.field[0] === selfScope?.value, // 左值是否取自本表单字段
        compare: c.compare,
        value: c.value,
        // _ops, _fieldType, _options 不持久化
      })),
  }
}

function render(rules: VisibilityRules | null) {
  if (rules && rules.conditions?.length) {
    formData.value.action = rules.action
    formData.value.condition = rules.condition
    formData.value.conditions = rules.conditions.map((c) => ({ id: c.id || randomId(), field: [c.field[0], c.field[1]], compare: c.compare, value: c.value }))
    formData.value.conditions.forEach((cond) => {
      if (cond.field && cond.field[0] && cond.field[1]) {
        const fieldType = inferFieldType(cond.field, props.leftOptions)
        const fieldConfig = getFieldConfig(cond.field, props.leftOptions)
        const isTreeMultiple = fieldType === 'TreeSelect' && fieldConfig?.attrs?.multiple
        const allowed = isTreeMultiple ? ['contain', 'not_contain'] : getAllowedOps(fieldType)
        cond._ops = compareList.filter((op) => allowed.includes(op.value))
        cond._fieldType = fieldType
        cond._options = fieldConfig?.option_list ?? []
        cond._treeData = fieldConfig?.attrs?.data ?? []
        cond._treeMultiple = isTreeMultiple
        const isMultiple = ['MultiSelect'].includes(fieldType || '') || isTreeMultiple
        // 清理脏数据
        if (cond.compare && !allowed.includes(cond.compare)) {
          cond.compare = ''
          cond.value = isMultiple ? [] : ''
        }
      }
    })
  }
}

defineExpose({ getData, render, validate })
</script>

<template>
  <div class="flex flex-col gap-4 w-full">
    <el-radio-group v-model="formData.action">
      <el-radio value="show">满足条件时显示</el-radio>
      <el-radio value="hide">满足条件时隐藏</el-radio>
    </el-radio-group>

    <div class="flex align-center gap-2">
      <span class="lighter">满足</span>
      <el-select v-model="formData.condition" size="small" class="w-20!">
        <el-option label="且" value="and" />
        <el-option label="或" value="or" />
      </el-select>
      <span class="lighter">条件</span>
    </div>

    <el-scrollbar>
      <div style="max-height: calc(100vh - 400px)">
        <MkFormList v-model="conditionRows" :default-item="defaultCondition" :first-row-has-label="false">
          <template #default="{ item: condition }">
            <ConditionRow :model-value="condition" :left-options="leftOptions" />
          </template>
        </MkFormList>
      </div>
    </el-scrollbar>
  </div>
</template>
