<script setup lang="ts">
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BaseNodeModel } from '@logicflow/core'
import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'NodeConditionDropdown' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ model: BaseNodeModel }>()
const emit = defineEmits<{
  'update:condition': [condition: boolean | 'AND' | 'OR']
  'visible-change': [visible: boolean]
}>()

interface NodeConditionProperties {
  condition?: boolean | 'AND' | 'OR'
  kind?: WorkflowKind
}

const nodeProperties = computed(() => props.model.properties as unknown as NodeConditionProperties)
const visible = computed(() => {
  return (
    ![
      WorkflowNodeType.Start,
      WorkflowNodeType.Base,
      WorkflowNodeType.ToolBaseNode,
      WorkflowNodeType.ToolStartNode,
      WorkflowNodeType.KnowledgeBase,
      WorkflowNodeType.LoopStartNode.toString(),
      WorkflowNodeType.DataSourceLocalNode,
      WorkflowNodeType.DataSourceWebNode,
    ].includes(String(props.model.type)) && nodeProperties.value.kind !== WorkflowKind.DataSource
  )
})
// 仅在执行条件可见且缺失时通知容器补齐，读取 computed 不写入节点。
watch(
  () => visible.value && !nodeProperties.value.condition,
  (needsDefault) => {
    if (needsDefault) emit('update:condition', 'AND')
  },
  { immediate: true },
)
const condition = computed({
  get: () => nodeProperties.value.condition || 'AND',
  set: (value: boolean | 'AND' | 'OR') => {
    emit('update:condition', value)
  },
})
</script>

<template>
  <MkDropdown v-if="visible" :teleported="false" trigger="click" placement="bottom" @visible-change="emit('visible-change', $event)">
    <el-button text>
      <MkIcon :name="condition === 'OR' ? 'icon_any_outlined' : 'icon_all_outlined'" :size="20" />
    </el-button>
    <template #dropdown>
      <div class="w-84 px-4 py-3">
        <h6>{{ t('workflow.node.executionCondition.title') }}</h6>
        <div class="mt-2 flex-align-center gap-2">
          <span>{{ t('workflow.node.executionCondition.prefix') }}</span>
          <el-select v-model="condition" size="small" class="w-15! shrink-0">
            <el-option :label="t('workflow.condition.match.all')" value="AND" />
            <el-option :label="t('workflow.condition.match.any')" value="OR" />
          </el-select>
          <span>{{ t('workflow.node.executionCondition.description') }}</span>
        </div>
      </div>
    </template>
  </MkDropdown>
</template>
