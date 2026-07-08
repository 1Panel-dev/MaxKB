<template>
  <div>
    <el-radio-group v-model="formData.action" class="mb-8">
      <el-radio value="show">{{
        $t('workflow.nodes.baseNode.visibilitySetting.showCondition')
      }}</el-radio>
      <el-radio value="hide">{{
        $t('workflow.nodes.baseNode.visibilitySetting.hideCondition')
      }}</el-radio>
    </el-radio-group>

    <div class="flex align-center mb-8">
      <span class="lighter">{{ $t('workflow.nodes.conditionNode.conditions.info') }}</span>
      <el-select v-model="formData.condition" size="small" style="width: 60px; margin: 0 8px">
        <el-option :label="$t('workflow.condition.AND')" value="and" />
        <el-option :label="$t('workflow.condition.OR')" value="or" />
      </el-select>
      <span class="lighter">{{ $t('workflow.nodes.conditionNode.conditions.label') }}</span>
    </div>

    <el-scrollbar>
      <div style="max-height: calc(100vh - 319px)">
        <ConditionRow
          v-for="(cond, idx) in formData.conditions"
          :key="cond.id"
          :cond="cond"
          :index="idx"
          :nodeModel="nodeModel"
          :currentNodeFields="currentNodeFields"
          :currentEditingIndex="currentEditingIndex"
          @delete="removeCondition(idx)"
        />
      </div>
    </el-scrollbar>

    <el-button link type="primary" @click="addCondition">
      <AppIcon iconName="app-add-outlined" class="mr-4" />
      {{ $t('common.add') }}
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
import { t } from '@/locales'
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
      cond._fieldError = t('workflow.variable.placeholder')
      hasError = true
    }
    if (!cond.compare) {
      cond._compareError = t('workflow.nodes.conditionNode.conditions.requiredMessage')
      hasError = true
    }
    const isEmpty = Array.isArray(cond.value)
      ? cond.value.length === 0
      : !cond.value && cond.value !== 0
    if (!['is_true', 'is_not_true'].includes(cond.compare) && isEmpty) {
      cond._valueError = t('workflow.nodes.conditionNode.valueMessage')
      hasError = true
    }
  }
  return hasError ? Promise.reject() : Promise.resolve()
}

function getData(): VisibilityRules | null {
  const conds = formData.value.conditions

  if (conds.length === 0) return null
  return {
    action: formData.value.action,
    condition: formData.value.condition,
    node_id: props.nodeModel?.id,
    node_name: props.nodeModel?.properties?.stepName,
    conditions: conds
      .filter((c) => c.field[0] && c.field[1] && c.compare)
      .map((c) => ({
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
        const fieldConfig = getFieldConfig(cond.field, props.nodeModel, props.currentNodeFields)
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

defineExpose({ getData, restore, validate })
</script>
<style lang="scss" scoped></style>
