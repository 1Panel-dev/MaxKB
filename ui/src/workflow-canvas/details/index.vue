<script setup lang="ts">
import { computed, type Component } from 'vue'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from './types'

defineOptions({ name: 'ExecutionDetailContent' })

const props = withDefaults(
  defineProps<{
    detail?: ExecutionNodeDetail[]
    workflowMode?: WorkflowMode
  }>(),
  {
    detail: () => [],
    workflowMode: WorkflowMode.Application,
  },
)

// 复用节点注册表：每个节点的 index.ts 默认导出携带注册的 WorkflowNodeType 及其执行详情视图
// details（各节点的整卡），与画布注册节点同源。据此建立 type -> 详情组件 映射，按节点类型渲染。
const nodeRegistryModules = import.meta.glob<{ default: { type: WorkflowNodeType; details?: Component } }>(
  '../nodes/*/index.ts',
  { eager: true },
)

const nodeDetailComponentMap: Map<WorkflowNodeType, Component> = (() => {
  const map = new Map<WorkflowNodeType, Component>()
  for (const { default: registration } of Object.values(nodeRegistryModules)) {
    if (registration?.details) map.set(registration.type, registration.details)
  }
  return map
})()

function nodeDetailComponent(type?: WorkflowNodeType): Component | null {
  return type ? (nodeDetailComponentMap.get(type) ?? null) : null
}

// 按 index 升序展示各节点执行详情。
const sortedDetail = computed(() =>
  [...props.detail].sort((a, b) => ((a?.index as number) || 0) - ((b?.index as number) || 0)),
)
</script>

<template>
  <div class="flex flex-col gap-2">
    <template v-for="(item, index) in sortedDetail" :key="index">
      <component
        :is="nodeDetailComponent(item.type)"
        v-if="nodeDetailComponent(item.type)"
        :data="item"
        :workflow-mode="workflowMode"
      />
    </template>
  </div>
</template>
