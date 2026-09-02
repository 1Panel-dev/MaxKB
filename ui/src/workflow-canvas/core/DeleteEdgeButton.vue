<script setup lang="ts">
import type { BaseEdgeModel } from '@logicflow/core'
import { inject } from 'vue'
const getModel = inject('getModel') as () => BaseEdgeModel
const model = getModel()
const deleteEdge = () => {
  model.graphModel.deleteEdgeById(model.id)
}
</script>
<template>
  <div class="workflow-node-delete-icon" @mouseup.stop @click.stop @click="deleteEdge">
    <MkIcon name="icon_close_bold_outlined" class="text-white!" />
  </div>
</template>
<style lang="scss">
.workflow-node-delete-icon {
  align-items: center;
  background: var(--el-color-primary);
  border-radius: 50%;
  display: flex;
  height: calc(var(--spacing) * 6);
  justify-content: center;
  opacity: 0;
  padding: 4px;
  pointer-events: none;
  transform-origin: center;
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
  width: calc(var(--spacing) * 6);
  z-index: 100000;
}
</style>
