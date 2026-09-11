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

// 新引擎节点详情的 status 为枚举字符串，而 v3 详情契约（types/DetailContainer/BaseHeader）统一使用
// v2 的数字状态码（200 成功 / 202 运行中 / 其余失败）。在详情进入 v3 渲染体系的唯一入口做一次适配，
// 已是数字（如历史数据或预览 mock）则原样透传。嵌套子节点会在递归渲染时经本入口再次适配。
const STATUS_CODE_MAP: Record<string, number> = {
  SUCCESS: 200,
  RUNNING: 202,
  BEFORE_RUNNING: 202,
  CANCELLED: 201,
  FAIL: 500,
}

function coerceStatus(status: unknown): number | undefined {
  if (typeof status === 'number') return status
  if (typeof status === 'string') return STATUS_CODE_MAP[status] ?? 500
  return status as undefined
}

// 按 index 升序展示各节点执行详情，并把枚举状态适配为数字状态码。
const sortedDetail = computed<ExecutionNodeDetail[]>(() =>
  [...props.detail]
    .sort((a, b) => ((a?.index as number) || 0) - ((b?.index as number) || 0))
    .map((item) => ({ ...item, status: coerceStatus(item.status) })),
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
