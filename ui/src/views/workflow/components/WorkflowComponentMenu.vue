<script setup lang="ts">
import { ref } from 'vue'

import { ClickOutside as vClickOutside } from 'element-plus'
import NodeMenu from '@/workflow-canvas/component/NodeMenu.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowComponentMenu' })

const emit = defineEmits<{ select: [nodeType: WorkflowNodeType] }>()

const popoverVisible = ref(false)

const handleSelect = (nodeType: WorkflowNodeType) => {
  emit('select', nodeType)
  popoverVisible.value = false
}
</script>

<template>
  <div v-click-outside="() => (popoverVisible = false)" class="relative">
    <el-button plain @click="popoverVisible = !popoverVisible"> 添加组件 </el-button>

    <el-collapse-transition>
      <NodeMenu v-show="popoverVisible" class="absolute right-0 top-[calc(100%+8px)] z-[2000]" @select="handleSelect" />
    </el-collapse-transition>
  </div>
</template>
