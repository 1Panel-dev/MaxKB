<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { randomId } from '@/utils/common'
import type { VisibilityRules } from '../../type'
import { inferFieldType, getAllowedOps, getFieldConfig } from './index'
import { compareList } from '@/workflow-canvas/config/constants'
import ConditionRow from './ConditionRow.vue'
import type { LeftOptions } from '../type'

defineOptions({ name: 'MkDynamicsFormVisibilityConstructor' })

const props = defineProps<{
  initialValue?: VisibilityRules | null
  leftOptions?: Array<LeftOptions>
}>()

const formData = ref({
  action: 'show' as 'show' | 'hide',
  condition: 'and' as 'and' | 'or',
  conditions: [] as Array<MkDynamicFormValue>,
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
    const isEmpty = Array.isArray(cond.value)
      ? cond.value.length === 0
      : !cond.value && cond.value !== 0
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
    formData.value.conditions = rules.conditions.map((c) => ({
      id: c.id || randomId(),
      field: [c.field[0], c.field[1]],
      compare: c.compare,
      value: c.value,
    }))
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

defineExpose({ getData, render, validate })
</script>

<template>
  <div>
    <el-radio-group v-model="formData.action" class="mb-8">
      <el-radio value="show">满足条件时显示</el-radio>
      <el-radio value="hide">满足条件时隐藏</el-radio>
    </el-radio-group>

    <div class="flex align-center mb-8">
      <span class="lighter">满足</span>
      <el-select v-model="formData.condition" size="small" style="width: 60px; margin: 0 8px">
        <el-option label="且" value="and" />
        <el-option label="或" value="or" />
      </el-select>
      <span class="lighter">条件</span>
    </div>

    <el-scrollbar>
      <div style="max-height: calc(100vh - 319px)">
        <ConditionRow
          v-for="(cond, idx) in formData.conditions"
          :key="cond.id"
          v-model="formData.conditions[idx]"
          :left-options="leftOptions"
          @delete="removeCondition(idx)"
        />
      </div>
    </el-scrollbar>

    <el-button link type="primary" @click="addCondition">
      <MkIcon name="icon_add_outlined" class="mr-4" />
      添加
    </el-button>
  </div>
</template>
