<script setup lang="ts">
import { ref } from 'vue'
import { RESOURCE_TYPE } from '@/api/enums'
import BasicNodeMenu from './BasicNodeMenu.vue'
import ResourceNodeMenu from './ResourceNodeMenu.vue'
import type { WorkflowMode } from '@/workflow-canvas/types'
import type { NodeMenuCurrentResource, NodeMenuItem, NodeMenuTab } from './types'

defineOptions({ name: 'NodeMenu' })

defineProps<{
  currentResource?: NodeMenuCurrentResource
  workflowMode: WorkflowMode
}>()

const emit = defineEmits<{
  dragstart: [node: NodeMenuItem, event: PointerEvent]
  select: [node: NodeMenuItem]
}>()

const activeTab = ref<NodeMenuTab>('basic')

function handleDragStart(node: NodeMenuItem, event: PointerEvent) {
  emit('dragstart', node, event)
}
</script>

<template>
  <div
    class="overflow-hidden rounded-xl border bg-white shadow-md"
    :class="activeTab === 'basic' ? 'w-[414px]' : 'w-[670px]'"
    @click.stop
    @mousedown.stop
    @mousemove.stop
  >
    <el-tabs v-model="activeTab" class="small p-4 pb-0">
      <el-tab-pane label="基础组件" name="basic" />
      <el-tab-pane label="工具" name="tool" />
      <el-tab-pane label="智能体" name="application" v-if="workflowMode === 'application'" />
    </el-tabs>

    <KeepAlive>
      <BasicNodeMenu
        v-if="activeTab === 'basic'"
        key="basic"
        :workflow-mode="workflowMode"
        @dragstart="handleDragStart"
        @select="emit('select', $event)"
      />

      <ResourceNodeMenu
        v-else
        :key="activeTab"
        :source="activeTab === 'tool' ? RESOURCE_TYPE.TOOL : RESOURCE_TYPE.APPLICATION"
        :current-resource="currentResource"
        @dragstart="handleDragStart"
        @select="emit('select', $event)"
      />
    </KeepAlive>
  </div>
</template>

<style lang="scss" scoped></style>
