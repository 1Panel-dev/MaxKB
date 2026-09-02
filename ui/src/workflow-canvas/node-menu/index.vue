<script setup lang="ts">
import { ref } from 'vue'
import { RESOURCE_TYPE } from '@/api/enums'
import BasicNodeMenu from './BasicNodeMenu.vue'
import ResourceNodeMenu from './ResourceNodeMenu.vue'
import type { NodeMenuItem, NodeMenuTab } from './types'

defineOptions({ name: 'NodeMenu' })

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
    class="overflow-hidden rounded-xl border bg-white shadow-md p-4 pb-0!"
    :class="activeTab === 'basic' ? 'w-[402px]' : 'w-[640px]'"
    @click.stop
    @mousedown.stop
    @mousemove.stop
  >
    <el-tabs v-model="activeTab" class="small">
      <el-tab-pane label="基础组件" name="basic">
        <BasicNodeMenu @dragstart="handleDragStart" @select="emit('select', $event)" />
      </el-tab-pane>
      <el-tab-pane label="工具" name="tool" lazy>
        <ResourceNodeMenu :source="RESOURCE_TYPE.TOOL" @dragstart="handleDragStart" @select="emit('select', $event)" />
      </el-tab-pane>
      <el-tab-pane label="智能体" name="application" lazy>
        <ResourceNodeMenu :source="RESOURCE_TYPE.APPLICATION" @dragstart="handleDragStart" @select="emit('select', $event)" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style lang="scss" scoped></style>
