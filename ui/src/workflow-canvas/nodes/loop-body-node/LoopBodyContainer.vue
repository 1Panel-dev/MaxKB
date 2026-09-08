<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import { iconComponent } from '@/workflow-canvas/icons/utils'

defineOptions({ name: 'WorkflowLoopBodyContainer' })
const props = defineProps<{ nodeModel: BaseNodeModel }>()
const model = computed(() => props.nodeModel)

const nodeSelected = ref(model.value.isSelected)
watch(
  () => model.value.isSelected,
  (value) => (nodeSelected.value = value),
)

const nodeStatus = computed(() => (model.value.properties.status as number | undefined) ?? 200)

const showNode = computed({
  get: () => {
    if (model.value.properties.showNode !== undefined) return model.value.properties.showNode
    set(model.value.properties, 'showNode', true)
    return true
  },
  set: (v) => set(model.value.properties, 'showNode', v),
})

// 循环体放大：按主画布视口和缩放计算尺寸，退出时恢复原尺寸。
const canvasHeight = ref(1000)
const stepContainerRef = ref<HTMLDivElement>()
const enlarge = ref(false)
let originalSize: { width: number; canvasHeight: number } | undefined

async function enlargeHandle() {
  const nodeModel = model.value
  const { graphModel } = nodeModel
  const { transformModel } = graphModel
  const stepContainer = stepContainerRef.value
  if (!stepContainer) return

  // 标题、边框和内边距由实际 DOM 测量，避免与容器样式重复维护。
  const chromeHeight = stepContainer.offsetHeight - (showNode.value ? canvasHeight.value : 0)

  if (enlarge.value && originalSize) {
    nodeModel.width = originalSize.width
    canvasHeight.value = originalSize.canvasHeight
    originalSize = undefined
    enlarge.value = false
  } else {
    const { width, height } = graphModel
    if (width <= 0 || height <= 0) return

    originalSize = { width: nodeModel.width, canvasHeight: canvasHeight.value }
    const viewportPadding = 16
    nodeModel.width = Math.max(1, (width - viewportPadding * 2) / transformModel.SCALE_X)
    canvasHeight.value = Math.max(1, (height - viewportPadding * 2) / transformModel.SCALE_Y - chromeHeight)
    showNode.value = true
    enlarge.value = true
  }

  nodeModel.properties.width = nodeModel.width
  await nextTick()
  nodeModel.setHeight(chromeHeight + (showNode.value ? canvasHeight.value : 0))
  if (enlarge.value) {
    transformModel.focusOn(nodeModel.x, nodeModel.y, graphModel.width, graphModel.height)
  }
}

function zoom() {
  if (enlarge.value) return enlargeHandle()
}

defineExpose({ zoom })
</script>

<template>
  <div class="workflow-node-container relative overflow-visible">
    <div ref="stepContainerRef" class="step-container p-4" :class="{ isSelected: nodeSelected, error: nodeStatus !== 200 }">
      <div class="flex-between">
        <div class="flex min-w-0 items-center gap-2">
          <component :is="iconComponent(`${model.type}-icon`)" class="mr-1" :size="24" :item="model.properties.node_data" />
          <h4 class="truncate break-all" :title="String(model.properties.stepName ?? '')">{{ model.properties.stepName }}</h4>
        </div>
        <div class="flex items-center gap-1" @pointerdown.stop @mousedown.stop @keydown.stop @click.stop>
          <el-button text :title="enlarge ? '还原' : '放大'" @click="enlargeHandle">
            <MkIcon name="icon_magnify_outlined" :size="20" />
          </el-button>
          <el-button text @click="showNode = !showNode">
            <MkIcon name="icon_down_outlined" :size="20" />
          </el-button>
        </div>
      </div>
      <el-collapse-transition>
        <div v-show="showNode" class="mt-4">
          <div :style="`height:${canvasHeight}px`"><slot /></div>
        </div>
      </el-collapse-transition>
    </div>
  </div>
</template>
<style lang="scss" scoped></style>
