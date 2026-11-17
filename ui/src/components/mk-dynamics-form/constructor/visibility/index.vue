<script setup lang="ts">
import { computed, ref } from 'vue'
import { I18nT, useI18n } from 'vue-i18n'
import type { VisibilityConditionState, VisibilityFieldOption, VisibilityRules } from '../../type'
import { compareList } from '@/workflow-canvas/config/constants'
import ConditionRow from './ConditionRow.vue'
import { getAllowedOps, getComparisonValueControl, getFieldConfig, inferFieldType } from './utils'
import { randomId } from '@/utils/common'
const { t } = useI18n({ useScope: 'global' })

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
    formData.value.conditions = conditions.map((condition) =>
      condition.id ? condition : { ...condition, id: randomId(), field: [...condition.field] as [string, string] },
    )
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
      cond._fieldError = t('dynamicForm.fields.variable.requiredMessage')
      hasError = true
    }
    if (!cond.compare) {
      cond._compareError = t('common.validation.selectRequired')
      hasError = true
    }
    const isEmpty = Array.isArray(cond.value) ? cond.value.length === 0 : !cond.value && cond.value !== 0
    if (!['is_true', 'is_not_true'].includes(cond.compare) && isEmpty) {
      cond._valueError =
        getComparisonValueControl(cond._fieldType) === 'input'
          ? t('dynamicForm.fields.comparisonValue.requiredMessage')
          : t('dynamicForm.fields.comparisonValue.selectRequiredMessage')
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

defineExpose({ getData, render, validate })
</script>

<template>
  <div class="w-full">
    <el-radio-group v-model="formData.action">
      <el-radio value="show">{{ t('dynamicForm.visibility.show') }}</el-radio>
      <el-radio value="hide">{{ t('dynamicForm.visibility.hide') }}</el-radio>
    </el-radio-group>

    <I18nT keypath="dynamicForm.visibility.match" tag="div" class="flex align-center gap-2 my-2" scope="global">
      <template #condition>
        <el-select v-model="formData.condition" size="small" class="w-20!">
          <el-option :label="t('dynamicForm.options.all')" value="and" />
          <el-option :label="t('dynamicForm.options.any')" value="or" />
        </el-select>
      </template>
    </I18nT>

    <MkFormList v-model="conditionRows" :default-item="defaultCondition" :firstRowHasLabel="false">
      <template #default="{ item: condition }">
        <ConditionRow :model-value="condition" :left-options="leftOptions" />
      </template>
    </MkFormList>
  </div>
</template>
