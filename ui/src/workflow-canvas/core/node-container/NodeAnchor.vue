<script setup lang="ts">
import { ref } from 'vue'
import type { Model } from '@logicflow/core'
import type { WorkflowNodeModel } from '../workflow-node'

defineOptions({ name: 'WorkflowNodeAnchor' })

const props = defineProps<{
  anchorData: Model.AnchorConfig
  canOpenNodeMenu: boolean
  connected: boolean
  nodeModel: WorkflowNodeModel
}>()
const tooltipSuppressed = ref(false)

function openNodeMenu() {
  tooltipSuppressed.value = true
  if (props.canOpenNodeMenu) props.nodeModel.openNodeMenu?.(props.anchorData)
}
</script>

<template>
  <el-tooltip :disabled="!canOpenNodeMenu || tooltipSuppressed" :enterable="false" placement="top">
    <template #content>点击添加节点<br />拖拽连接节点</template>
    <div
      class="workflow-node-anchor"
      :class="{
        'is-right': anchorData.type === 'right',
        'is-connected': connected,
        'is-abnormal': anchorData.id?.endsWith('_exception_right'),
      }"
      :data-node-menu-node-id="nodeModel.id"
      :data-node-menu-anchor-id="anchorData.id"
      @click="openNodeMenu"
      @pointerdown="tooltipSuppressed = true"
      @mouseleave="tooltipSuppressed = false"
    >
      <MkIcon v-if="!connected || anchorData.type === 'right'" name="icon_add_bold_outlined" class="text-white!" :size="12" />
    </div>
  </el-tooltip>
</template>
