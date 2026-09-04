<script setup lang="ts">
import { ref } from 'vue'

import { ClickOutside as vClickOutside } from 'element-plus'
import NodeMenu from '@/workflow-canvas/node-menu/index.vue'
import type { NodeMenuItem } from '@/workflow-canvas/node-menu/types'
import type { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowComponentMenu' })

defineProps<{
  workflowMode: WorkflowMode
}>()

const emit = defineEmits<{
  dragstart: [node: NodeMenuItem, event: PointerEvent]
  select: [node: NodeMenuItem]
}>()

const popoverVisible = ref(false)
const dragClosing = ref(false)

const togglePopover = () => {
  dragClosing.value = false
  popoverVisible.value = !popoverVisible.value
}

const handleSelect = (node: NodeMenuItem) => {
  emit('select', node)
  popoverVisible.value = false
}

const handleDragStart = (node: NodeMenuItem, event: PointerEvent) => {
  emit('dragstart', node, event)
  dragClosing.value = true
  popoverVisible.value = false
}
</script>

<template>
  <div v-click-outside="() => (popoverVisible = false)" class="relative">
    <el-button plain @click="togglePopover"> 添加组件 </el-button>

    <el-collapse-transition>
      <NodeMenu
        v-show="popoverVisible"
        class="absolute right-0 top-[calc(100%+8px)] z-[2000]"
        :class="{ 'pointer-events-none': dragClosing }"
        :workflow-mode="workflowMode"
        @dragstart="handleDragStart"
        @select="handleSelect"
      />
    </el-collapse-transition>
  </div>
</template>
