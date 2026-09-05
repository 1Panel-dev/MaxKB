<script setup lang="ts">
import { ref } from 'vue'
import { ClickOutside as vClickOutside } from 'element-plus'
import NodeMenu from '@/workflow-canvas/node-menu/index.vue'
import type { NodeMenuItem } from '@/workflow-canvas/node-menu/types'
import type { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowNodeAdd' })

defineProps<{
  workflowMode: WorkflowMode
}>()

const emit = defineEmits<{
  dragstart: [node: NodeMenuItem, event: PointerEvent]
  select: [node: NodeMenuItem]
}>()

const menuVisible = ref(false)
const dragClosing = ref(false)

function toggleMenu() {
  dragClosing.value = false
  menuVisible.value = !menuVisible.value
}

function handleSelect(node: NodeMenuItem) {
  emit('select', node)
  menuVisible.value = false
}

function handleDragStart(node: NodeMenuItem, event: PointerEvent) {
  emit('dragstart', node, event)
  dragClosing.value = true
  menuVisible.value = false
}
</script>

<template>
  <div v-click-outside="() => (menuVisible = false)" class="relative">
    <el-tooltip content="添加组件" placement="left">
      <el-button text @click="toggleMenu">
        <MkIcon name="icon_more-add_filled" :size="18" />
      </el-button>
    </el-tooltip>

    <el-collapse-transition>
      <NodeMenu
        v-show="menuVisible"
        class="absolute -top-2 left-10 z-20"
        :class="{ 'pointer-events-none': dragClosing }"
        :workflow-mode="workflowMode"
        @dragstart="handleDragStart"
        @select="handleSelect"
      />
    </el-collapse-transition>
  </div>
</template>
