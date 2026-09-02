<script setup lang="ts">
import { ref } from 'vue'

import { ClickOutside as vClickOutside } from 'element-plus'
import NodeMenu from '@/workflow-canvas/component/NodeMenu.vue'
import type { WorkflowMenuNode } from '@/workflow-canvas/config/menu'

defineOptions({ name: 'WorkflowComponentMenu' })

const emit = defineEmits<{
  dragstart: [workflowNode: WorkflowMenuNode, event: PointerEvent]
  select: [workflowNode: WorkflowMenuNode]
}>()

const popoverVisible = ref(false)
const dragClosing = ref(false)

const togglePopover = () => {
  dragClosing.value = false
  popoverVisible.value = !popoverVisible.value
}

const handleSelect = (workflowNode: WorkflowMenuNode) => {
  emit('select', workflowNode)
  popoverVisible.value = false
}

const handleDragStart = (workflowNode: WorkflowMenuNode, event: PointerEvent) => {
  emit('dragstart', workflowNode, event)
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
        @dragstart="handleDragStart"
        @select="handleSelect"
      />
    </el-collapse-transition>
  </div>
</template>
