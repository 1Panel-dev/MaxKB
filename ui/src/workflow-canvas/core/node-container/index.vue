<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { reaction } from '@logicflow/core'
import { cloneDeep, escape, escapeRegExp } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { NodeMenuItem } from '@/workflow-canvas/node-menu/types'
import type { WorkflowNodeField } from '@/workflow-canvas/types'
import type { BaseNodeModel, Model } from '@logicflow/core'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import NodeMenu from '@/workflow-canvas/node-menu/index.vue'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import NodeConditionDropdown from './NodeConditionDropdown.vue'
import NodeOperateDropdown from './NodeOperateDropdown.vue'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'NodeContainer' })

const { t } = useI18n({ useScope: 'global' })

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
    WorkflowNodeType.Llm,
    WorkflowNodeType.VideoUnderstandNode,
    WorkflowNodeType.ImageGenerateNode,
    WorkflowNodeType.ImageUnderstandNode,
  ],
})
const getModel = inject('getModel') as () => BaseNodeModel
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
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
  return nodeProperties.value.config?.output_title ?? t('execution.details.outputParams')
})

const abnormalNodeFields = computed(() => {
  return [
    {
      label: t('workflow.node.exception.messageLabel'),
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
  // 将所属节点置顶，避免添加菜单被其他节点遮挡。
  model.graphModel.toFront(model.id)
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
  if (!keyWord.value) return escape(contentText)
  const keywordPattern = new RegExp(`(${escapeRegExp(keyWord.value)})`, 'gi')
  return contentText
    .split(keywordPattern)
    .map((part, index) => {
      const text = escape(part)
      if (index % 2 === 0) return text
      return currentKeyWord.value ? `<span style='background: var(--mk-warning);'>${text}</span>` : `<span style='background: #FFC60A'>${text}</span>`
    })
    .join('')
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
  <div class="workflow-node-container relative overflow-visible" @mousedown="handleNodeMousedown" @wheel="handleNodeWheel">
    <div ref="stepContainerRef" class="step-container p-4" :class="{ isSelected: nodeSelected, error: node_status !== 200 }">
      <div>
        <div class="flex-between">
          <div class="flex-align-center min-w-0 flex-1" @dragstart.prevent @drag.prevent @dragover.prevent @dragend.prevent>
            <component :is="iconComponent(`${model.type}-icon`)" class="mr-2 shrink-0" :size="24" :item="model?.properties.node_data" />
            <h4
              class="truncate"
              :title="String(model.properties.stepName ?? '')"
              v-html="highlightedStepName(String(model.properties.stepName ?? ''))"
            ></h4>
          </div>

          <div class="flex-align-center shrink-0 gap-1" @pointerdown.stop @mousemove.stop @mousedown.stop @keydown.stop @click.stop>
            <!-- 展开或收起节点 -->
            <el-button text @click="showNode = !showNode">
              <MkIcon :name="showNode ? 'icon_up_outlined' : 'icon_down_outlined'" :size="20" />
            </el-button>
            <NodeConditionDropdown
              :model="model"
              @update:condition="model.properties.condition = $event"
              @visible-change="anchorGuard.setOverlayVisible('condition', $event)"
            />
            <NodeOperateDropdown
              :model="model"
              @update:disabled="model.properties.disabled = $event"
              @update:step-name="model.properties.stepName = $event"
              @visible-change="anchorGuard.setOverlayVisible('operate', $event)"
            />
          </div>
        </div>

        <el-alert v-if="nodeDisabled" class="mt-4!" :title="t('workflow.node.disabledMessage')" type="error" show-icon :closable="false" />
        <el-alert
          v-if="node_status != 200"
          class="mt-4!"
          :title="
            String(model.type) === WorkflowNodeType.Application
              ? t('workflow.node.applicationUnavailableMessage')
              : t('workflow.node.toolUnavailableMessage')
          "
          type="error"
          show-icon
          :closable="false"
        />

        <el-collapse-transition>
          <div v-show="showNode" class="mt-4" @pointerdown.stop @pointermove.stop @pointerenter.stop @mousedown.stop @keydown.stop @click.stop>
            <slot />

            <!-- 输出参数 -->
            <template v-if="nodeFields.length > 0">
              <div class="flex-between mt-2 gap-2">
                <h6 class="mk-title-decoration my-2 shrink-0">{{ output_title }}</h6>
                <div v-if="exceptionNodeList.includes(String(model.type))" class="min-w-0 flex flex-1 flex-wrap items-center justify-end gap-2">
                  <span class="whitespace-nowrap">{{ t('workflow.node.exception.label') }}</span>
                  <el-switch v-model="enable_exception" class="shrink-0" size="small" />
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
        :workflow-mode="workflowMode"
        @pointerdown.stop
        @mousemove.stop
        @mousedown.stop
        @click.stop
        @wheel="handleNodeWheel"
        style="left: 105%; transform: translate(0, -50%)"
        :style="dropdownMenuStyle"
        @select="clickNodes"
      />
    </el-collapse-transition>
  </div>
</template>
<style lang="scss" scoped></style>
