<script setup lang="ts">
import { reaction, type BaseNodeModel, type Model } from '@logicflow/core'
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { cloneDeep } from 'lodash'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import { copyText } from '@/utils/clipboard'
import { WorkflowMode, WorkflowNodeType, type ShapeItem, type WorkflowNodeField } from '@/workflow-canvas/types'
import NodeMenu from '@/workflow-canvas/node-menu/index.vue'
import type { NodeMenuCurrentResource, NodeMenuItem } from '@/workflow-canvas/node-menu/types'
import NodeConditionDropdown from './NodeConditionDropdown.vue'
import NodeOperateDropdown from './NodeOperateDropdown.vue'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'

defineOptions({ name: 'NodeContainer' })

type NodeContainerProperties = {
  config?: { fields?: WorkflowNodeField[]; output_title?: string }
  disabled?: boolean
  enableException?: boolean
  showNode?: boolean
  status?: number
}

withDefaults(defineProps<{ exceptionNodeList?: string[] }>(), {
  exceptionNodeList: () => [
    WorkflowNodeType.AiChat,
    WorkflowNodeType.VideoUnderstandNode,
    WorkflowNodeType.ImageGenerateNode,
    WorkflowNodeType.ImageUnderstandNode,
  ],
})
const getModel = inject('getModel') as () => BaseNodeModel
const startDragNode = inject<(shapeItem: ShapeItem, event?: PointerEvent) => void>('startDragNode')
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const currentResource = inject<NodeMenuCurrentResource>('currentResource')
const model = getModel()
const nodeProperties = computed(() => model.properties as unknown as NodeContainerProperties)
const nodeSelected = ref(model.isSelected)
const disposeSelectionReaction = reaction(
  () => model.isSelected,
  (isSelected) => {
    nodeSelected.value = isSelected
  },
)

const showAnchor = ref(false)
const nodeMenuDragClosing = ref(false)
const nodeMenuRef = ref<InstanceType<typeof NodeMenu>>()
const anchorData = ref<Model.AnchorConfig>()
const dropdownMenuStyle = computed(() => {
  return { top: anchorData.value ? anchorData.value.y - model.y + model.height / 2 + 'px' : '0px' }
})
const nodeDisabled = computed({
  get: () => {
    return model.properties.disabled || false
  },
  set: (v: boolean) => {
    model.properties.disabled = v
  },
})
const anchorGuard = createAnchorGuard(model)

if (model.properties.showNode === undefined) {
  model.properties.showNode = true
}
const showNode = computed({
  set: (v) => {
    model.properties.showNode = v
  },
  get: () => model.properties.showNode ?? true,
})

const node_status = computed(() => {
  if (model.properties.status) {
    return model.properties.status
  }
  return 200
})

const handleNodeMousedown = (event?: MouseEvent) => {
  if (!event?.shiftKey) {
    model.graphModel.clearSelectElements()
  }
  model.isSelected = !model.isSelected
  model.isHovered = !model.isSelected
  model.graphModel.toFront(model.id)
}
const resizeStepContainer = (nodeHeight: number) => {
  if (nodeHeight > 0 && !model.virtual) {
    model.setHeight(nodeHeight)
  }
}

function clickNodes(item: NodeMenuItem) {
  const anchor = anchorData.value
  if (!anchor || !item.type) return

  const width = Number(item.properties?.width ?? 214)
  const height = Number(item.height ?? item.properties?.height ?? 0)
  const newModel = model.graphModel.addNode({
    type: item.type,
    properties: cloneDeep(item.properties ?? {}),
    x: anchor.x + width / 2 + 200,
    y: anchor.y - height,
  })
  newModel.graphModel.addEdge({
    type: 'app-edge',
    sourceNodeId: model.id,
    sourceAnchorId: anchor.id,
    targetNodeId: newModel.id,
    targetAnchorId: newModel.id + '_left',
  })

  closeNodeMenu()
}

function dragNode(item: NodeMenuItem, event: PointerEvent) {
  startDragNode?.(item, event)
  nodeMenuDragClosing.value = true
  closeNodeMenu()
}
if (model.properties.enableException === undefined) {
  model.properties.enableException = false
}
const enable_exception = computed({
  set: (v) => {
    model.properties.enableException = v
  },
  get: () => model.properties.enableException ?? false,
})
const nodeFields = computed(() => {
  if (nodeProperties.value.config?.fields) {
    const fields = nodeProperties.value.config.fields.map((field) => {
      return {
        label: field.label,
        value: field.value,
        globeLabel: `{{${model.properties.stepName}.${field.value}}}`,
        globeValue: `{{context['${model.id}'].${field.value}}}`,
      }
    })
    return fields
  }
  return []
})

const output_title = computed(() => {
  return nodeProperties.value.config?.output_title ?? '输出参数'
})

const abnormalNodeFields = computed(() => {
  return [
    {
      label: '异常信息',
      value: 'exception_message',
      globeLabel: `{{${model.properties.stepName}.exception_message}}`,
      globeValue: `{{context['${model.id}'].exception_message}}`,
    },
  ]
})
watch(enable_exception, () => {
  model.graphModel.eventCenter.emit(
    'delete_edge',
    model.outgoing.edges.filter((item) => item.sourceAnchorId === `${model.id}_exception_right`).map((item) => item.id),
  )
})

const openNodeMenu = (anchorValue: Model.AnchorConfig) => {
  nodeMenuDragClosing.value = false
  showAnchor.value = true
  anchorData.value = anchorValue
  model.graphModel.rootEl.addEventListener('pointerdown', handleNodeMenuOutsidePointerDown, true)
}
const closeNodeMenu = () => {
  model.graphModel.rootEl.removeEventListener('pointerdown', handleNodeMenuOutsidePointerDown, true)
  showAnchor.value = false
  anchorData.value = undefined
}
/**
 * 检索选中时候触发
 * @param kw
 */

const keyWord = ref('')
const currentKeyWord = ref(false)
const selectOn = (kw: string) => {
  keyWord.value = kw
  model.setSelected(false)
  currentKeyWord.value = false
}

// 捕获阶段处理外部点击，避免节点表单和画布交互停止冒泡后菜单无法关闭。
const handleNodeMenuOutsidePointerDown = (event: PointerEvent) => {
  const target = event.target
  if (!(target instanceof Element) || nodeMenuRef.value?.$el.contains(target)) return

  const anchorElement = target.closest('[data-node-menu-anchor-id]')
  if (
    anchorElement?.getAttribute('data-node-menu-node-id') === model.id &&
    anchorElement.getAttribute('data-node-menu-anchor-id') === anchorData.value?.id
  ) {
    return
  }

  closeNodeMenu()
}
/**
 * 定位时触发
 * @param kw
 */
const focusOn = () => {
  model.setSelected(true)
  currentKeyWord.value = true
}
/**
 * 清除时触发
 */
const clearSelectOn = () => {
  keyWord.value = ''
  currentKeyWord.value = false
}

// 高亮选中关键字

const highlightedStepName = (contentText: string) => {
  let res = contentText
  if (keyWord.value === '') {
    return res
  } else {
    const wordsArray = contentText.split('')
    for (let i = 0; i < wordsArray.length; i++) {
      const word = wordsArray[i]
      if (word && keyWord.value.includes(word)) {
        wordsArray[i] = currentKeyWord.value
          ? `<span style='background: #FF8800;'>${word}</span>`
          : `<span style='background: #FFC60A;'>${word}</span>`
      }
    }
    res = wordsArray.join('')
    return res
  }
}
onMounted(() => {
  model.openNodeMenu = (anchor: Model.AnchorConfig) => {
    showAnchor.value && anchorData.value?.id === anchor.id ? closeNodeMenu() : openNodeMenu(anchor)
  }
  model.selectOn = selectOn
  model.focusOn = focusOn
  model.clearSelectOn = clearSelectOn
  initResizeObserver()
})
let resizeObserver: ResizeObserver | null = null
const initResizeObserver = () => {
  if (!stepContainerRef.value) return

  resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const nodeHeight = entry.borderBoxSize[0]?.blockSize ?? (entry.target as HTMLElement).offsetHeight
      resizeStepContainer(nodeHeight)
    }
  })

  resizeObserver.observe(stepContainerRef.value)
}
const stepContainerRef = ref<HTMLElement>()
onBeforeUnmount(() => {
  closeNodeMenu()
  model.openNodeMenu = undefined
  disposeSelectionReaction()
  resizeObserver?.disconnect()
  resizeObserver = null
  anchorGuard.reset()
})
</script>
<template>
  <div class="workflow-node-container relative overflow-visible" @mousedown="handleNodeMousedown">
    <div
      ref="stepContainerRef"
      class="step-container shadow-sm overflow-visible rounded-xl border-2 border-white bg-white p-4"
      :class="{ isSelected: nodeSelected, error: node_status !== 200 }"
    >
      <div>
        <div class="flex-between">
          <div class="flex items-center" @dragstart.prevent @drag.prevent @dragover.prevent @dragend.prevent>
            <component :is="iconComponent(`${model.type}-icon`)" class="mr-2" :size="24" :item="model?.properties.node_data" />
            <h4
              class="truncate break-all"
              :title="String(model.properties.stepName ?? '')"
              v-html="highlightedStepName(String(model.properties.stepName ?? ''))"
            ></h4>
          </div>

          <div class="flex items-center gap-1" @mousemove.stop @mousedown.stop @keydown.stop @click.stop>
            <el-button text @click="showNode = !showNode">
              <MkIcon name="icon_down_outlined" />
            </el-button>
            <NodeConditionDropdown :model="model" @visible-change="anchorGuard.setOverlayVisible('condition', $event)" />
            <NodeOperateDropdown :model="model" @visible-change="anchorGuard.setOverlayVisible('operate', $event)" />
          </div>
        </div>

        <el-alert v-if="nodeDisabled" class="mt-4!" title="该节点已禁用" type="error" show-icon :closable="false" />
        <el-alert
          v-if="node_status != 200"
          class="mt-4!"
          :title="String(model.type) === WorkflowNodeType.Application ? '该智能体不可用' : '该工具不可用'"
          type="error"
          show-icon
          :closable="false"
        />

        <el-collapse-transition>
          <div v-show="showNode" class="mt-4" @pointermove.stop @pointerenter.stop @mousedown.stop @keydown.stop @click.stop>
            <slot />

            <!-- 输出参数 -->
            <template v-if="nodeFields.length > 0">
              <div class="flex-between">
                <h6 class="mk-title-decoration my-2">{{ output_title }}</h6>
                <div v-if="exceptionNodeList.includes(String(model.type))" class="flex items-center gap-2">
                  <span>异常捕获</span>
                  <el-switch v-model="enable_exception" size="small" />
                </div>
              </div>
              <div class="mk-gray-card space-y-4">
                <template v-for="(item, index) in nodeFields" :key="index">
                  <div class="group flex-between">
                    <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>
                    <el-button class="group-hover-visible" link @click="copyText(item.globeLabel)">
                      <MkIcon name="icon_copy_outlined" />
                    </el-button>
                  </div>
                </template>
              </div>

              <div v-if="enable_exception" class="mk-gray-card space-y-4 mt-1">
                <template v-for="(item, index) in abnormalNodeFields" :key="index">
                  <div class="group flex-between">
                    <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>

                    <el-button class="group-hover-visible" link @click="copyText(item.globeLabel)">
                      <MkIcon name="icon_copy_outlined" />
                    </el-button>
                  </div>
                </template>
              </div>
            </template>
          </div>
        </el-collapse-transition>
      </div>
    </div>

    <el-collapse-transition>
      <NodeMenu
        v-if="showAnchor"
        ref="nodeMenuRef"
        class="absolute"
        :class="{ 'pointer-events-none': nodeMenuDragClosing }"
        :current-resource="currentResource"
        :workflow-mode="workflowMode"
        @mousemove.stop
        @mousedown.stop
        @click.stop
        @wheel="handleNodeWheel"
        style="left: 105%; transform: translate(0, -50%)"
        :style="dropdownMenuStyle"
        @dragstart="dragNode"
        @select="clickNodes"
      />
    </el-collapse-transition>
  </div>
</template>
<style lang="scss" scoped>
.workflow-node-container {
  .step-container {
    box-sizing: border-box;
    &:hover {
      box-shadow: 0px 6px 24px 0px rgb(var(--mk-N900-rgb) / 8%);
    }

    &.isSelected {
      border-color: var(--mk-primary);
    }

    &.error {
      border-color: var(--mk-danger);
      border-width: 1px;
    }
  }
}
</style>
