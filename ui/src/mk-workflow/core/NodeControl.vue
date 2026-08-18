<script setup lang="ts">
import { FullScreen, ZoomIn, ZoomOut } from '@element-plus/icons-vue'
import type LogicFlow from '@logicflow/core'

defineOptions({ name: 'WorkflowNodeControl' })

const props = defineProps<{ logicFlow: LogicFlow }>()

function fitView() {
  props.logicFlow.resetZoom()
  props.logicFlow.resetTranslate()
  props.logicFlow.fitView(40, 40)
}
</script>

<template>
  <div
    class="absolute bottom-5 left-5 z-10 flex rounded-lg border border-N300 bg-white p-1 shadow-sm"
  >
    <el-tooltip content="缩小" placement="top">
      <el-button text @click="props.logicFlow.zoom(false)"><MkIcon :icon="ZoomOut" /></el-button>
    </el-tooltip>
    <el-tooltip content="放大" placement="top">
      <el-button text @click="props.logicFlow.zoom(true)"><MkIcon :icon="ZoomIn" /></el-button>
    </el-tooltip>
    <el-tooltip content="适应画布" placement="top">
      <el-button text @click="fitView"><MkIcon :icon="FullScreen" /></el-button>
    </el-tooltip>
  </div>
</template>
