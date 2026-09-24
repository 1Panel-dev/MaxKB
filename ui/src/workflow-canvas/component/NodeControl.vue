<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import type LogicFlow from '@logicflow/core'
import type { BaseNodeModel } from '@logicflow/core'
import type { SelectionSelect } from '@logicflow/extension'
import type Dagre from '@/workflow-canvas/plugins/dagre'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowNodeControl' })

const props = defineProps<{ logicFlow: LogicFlow }>()
type ControlExtensions = { selectionSelect: SelectionSelect; dagre: Dagre }
type LoopLayoutNode = BaseNodeModel & { loopLayout?: () => void | Promise<unknown> }

// 框选与平移只作用于当前画布，保留节点自身的编辑和拖拽。
const selectionMode = ref(false)

function changeCursor(select: boolean) {
  const { selectionSelect } = props.logicFlow.extension as ControlExtensions
  if (select) {
    selectionSelect.setSelectionSense(true, false)
    selectionSelect.openSelectionSelect()
  } else {
    selectionSelect.closeSelectionSelect()
  }
  selectionMode.value = select
  const canvas = props.logicFlow.container.querySelector<HTMLElement>('.lf-drag-able')
  if (canvas) canvas.style.cursor = select ? 'default' : 'grab'
}

// 缩放读数同时响应工具栏、滚轮及适应视口操作。
const scale = ref(1)
const minScale = ref(0.2)
const maxScale = ref(16)
const hasNodes = ref(false)
const layoutLoading = ref(false)

watch(
  () => props.logicFlow,
  (logicFlow, _, onCleanup) => {
    const syncCanvasState = () => {
      const transform = logicFlow.graphModel.transformModel
      scale.value = transform.SCALE_X
      minScale.value = transform.MINI_SCALE_SIZE
      maxScale.value = transform.MAX_SCALE_SIZE
      hasNodes.value = logicFlow.graphModel.nodes.length > 0
    }
    const events = 'graph:transform,graph:rendered,node:add,node:delete'
    syncCanvasState()
    changeCursor(false)
    logicFlow.on(events, syncCanvasState)
    onCleanup(() => {
      logicFlow.off(events, syncCanvasState)
      const { selectionSelect } = logicFlow.extension as ControlExtensions
      selectionSelect.closeSelectionSelect()
    })
  },
  { immediate: true, flush: 'post' },
)

function zoomTo(nextScale: number) {
  const { graphModel, container } = props.logicFlow
  const center = graphModel.transformModel.HtmlPointToCanvasPoint([container.clientWidth / 2, container.clientHeight / 2])
  props.logicFlow.zoom(Math.min(maxScale.value, Math.max(minScale.value, nextScale)), center)
}

function zoom(direction: 1 | -1) {
  zoomTo(scale.value + direction * props.logicFlow.graphModel.transformModel.ZOOM_SIZE)
}

function fitView() {
  props.logicFlow.fitView(40, 40)
}

// 批量展开收起不替换节点数据，保留表单内容。
function setNodesExpanded(expanded: boolean) {
  props.logicFlow.graphModel.nodes.forEach((node) => {
    node.properties.showNode = expanded
  })
}

async function layout() {
  if (layoutLoading.value || !hasNodes.value) return
  layoutLoading.value = true
  const logicFlow = props.logicFlow
  try {
    await Promise.all(
      logicFlow.graphModel.nodes
        .filter((node) => String(node.type) === WorkflowNodeType.LoopBodyNode)
        .map((node) => (node as LoopLayoutNode).loopLayout?.()),
    )
    await nextTick()
    await (logicFlow.extension as ControlExtensions).dagre.layout()
  } catch {
    MsgError('自动布局失败，请重试')
  } finally {
    layoutLoading.value = false
  }
}
</script>

<template>
  <el-card class="absolute bottom-4 right-4 z-10" shadow="always" style="--el-card-padding: 8px" @pointerdown.stop @wheel.stop>
    <div class="flex-align-center gap-2">
      <!-- 切换为框选节点 -->
      <el-button
        text
        :class="selectionMode ? 'bg-primary/10! text-primary!' : 'text-N600!'"
        :aria-pressed="selectionMode"
        @click="changeCursor(true)"
      >
        <MkIcon name="icon_cursor_outlined" :size="18" />
      </el-button>

      <!-- 切换为拖动画布 -->
      <el-button
        text
        :class="!selectionMode ? 'bg-primary/10! text-primary!' : 'text-N600!'"
        :aria-pressed="!selectionMode"
        @click="changeCursor(false)"
      >
        <MkIcon name="icon_raisehand_outlined" :size="18" />
      </el-button>

      <el-divider direction="vertical" class="mx-1!" />

      <MkTooltip content="缩小" placement="top">
        <!-- 缩小画布 -->
        <el-button text @click="zoom(-1)">
          <MkIcon name="icon_zoom-out_outlined" :size="18" />
        </el-button>
      </MkTooltip>

      <MkTooltip content="放大" placement="top">
        <!-- 放大画布 -->
        <el-button text @click="zoom(1)">
          <MkIcon name="icon_zoom-in_outlined" :size="18" />
        </el-button>
      </MkTooltip>
      <MkTooltip content="适应" placement="top">
        <!-- 显示全部节点 -->
        <el-button text @click="fitView">
          <MkIcon name="icon_repositioning_outlined" :size="18" />
        </el-button>
      </MkTooltip>

      <el-divider direction="vertical" class="mx-1!" />

      <MkTooltip content="收起全部节点" placement="top">
        <!-- 收起全部节点 -->
        <el-button text @click="setNodesExpanded(false)">
          <MkIcon name="icon_collapse_outlined" :size="18" />
        </el-button>
      </MkTooltip>
      <MkTooltip content="展开全部节点" placement="top">
        <!-- 展开全部节点 -->
        <el-button text @click="setNodesExpanded(true)">
          <MkIcon name="icon_expand_outlined" :size="18" />
        </el-button>
      </MkTooltip>
      <MkTooltip content="一键美化" placement="top">
        <!-- 自动整理节点位置 -->
        <el-button text @click="layout">
          <MkIcon name="icon_effects_outlined" :size="18" />
        </el-button>
      </MkTooltip>
    </div>
  </el-card>
</template>
