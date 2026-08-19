<script setup lang="ts">
import type { Model } from '@logicflow/core'
import { ArrowDownBold, CircleCheck } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted, watch } from 'vue'
import { set } from 'lodash'
import { iconComponent } from '../icons/utils'
import { copyText } from '@/utils/clipboard'
import { WorkflowNodeType, WorkflowKind, type WorkflowNodeField } from '@/workflow-canvas/types'
import { MsgError, MsgConfirm } from '@/utils/message'
import { BasicComponentsNode } from '@/workflow-canvas/config/node-mapping'
import NodeMenu from '@/workflow-canvas/component/NodeMenu.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'

interface NodeNameForm {
  title: string
}

interface ResizeSize {
  height: number
}

type NodeContainerProperties = {
  condition?: boolean | 'AND' | 'OR'
  config?: {
    fields?: WorkflowNodeField[]
    output_title?: string
  }
  disabled?: boolean
  enableException?: boolean
  kind?: WorkflowKind
  node_data?: {
    name?: string
  }
  showNode?: boolean
  status?: number
  stepName?: string
}

const props = withDefaults(
  defineProps<{
    nodeModel: WorkflowNodeModel
    exceptionNodeList?: string[]
  }>(),
  {
    exceptionNodeList: () => [
      WorkflowNodeType.AiChat,
      WorkflowNodeType.VideoUnderstandNode,
      WorkflowNodeType.ImageGenerateNode,
      WorkflowNodeType.ImageUnderstandNode,
    ],
  },
)
const nodeProperties = computed(
  () => props.nodeModel.properties as unknown as NodeContainerProperties,
)

const height = ref<{
  stepContainerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContainerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0,
})
const showAnchor = ref(false)
const anchorData = ref<Model.AnchorConfig>()
const dropdownMenuStyle = computed(() => {
  return {
    top: anchorData.value
      ? anchorData.value.y - props.nodeModel.y + props.nodeModel.height / 2 + 'px'
      : '0px',
  }
})
const nodeDisabled = computed({
  get: () => {
    return props.nodeModel.properties.disabled || false
  },
  set: (v: boolean) => {
    set(props.nodeModel.properties, 'disabled', v)
  },
})
const nodeEnabled = computed({
  get: () => !nodeDisabled.value,
  set: (v: boolean) => {
    nodeDisabled.value = !v
  },
})
const titleFormRef = useTemplateRef<FormInstance>('titleFormRef')
const nodeNameDialogVisible = ref(false)
const form = ref<NodeNameForm>({
  title: '',
})

const condition = computed({
  set: (v) => {
    set(props.nodeModel.properties, 'condition', v)
  },
  get: () => {
    if (props.nodeModel.properties.condition) {
      return props.nodeModel.properties.condition
    }
    set(props.nodeModel.properties, 'condition', 'AND')
    return true
  },
})
const showNode = computed({
  set: (v) => {
    set(props.nodeModel.properties, 'showNode', v)
  },
  get: () => {
    if (props.nodeModel.properties.showNode !== undefined) {
      return props.nodeModel.properties.showNode
    }
    set(props.nodeModel.properties, 'showNode', true)
    return true
  },
})

const node_status = computed(() => {
  if (props.nodeModel.properties.status) {
    return props.nodeModel.properties.status
  }
  return 200
})

const sourceName = computed(() => {
  if (
    [WorkflowNodeType.Application, WorkflowNodeType.ToolLib].includes(
      String(props.nodeModel.type) as WorkflowNodeType,
    )
  ) {
    return nodeProperties.value.node_data?.name || ''
  }
  return ''
})

function renameNode() {
  form.value.title = String(props.nodeModel.properties.stepName ?? '')
  nodeNameDialogVisible.value = true
}
const editName = async (formEl: FormInstance | null | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      if (
        !props.nodeModel.graphModel.nodes
          .filter((node) => node.id !== props.nodeModel.id)
          .some((node) => node.properties.stepName === form.value.title)
      ) {
        set(props.nodeModel.properties, 'stepName', form.value.title)
        props.nodeModel.clearNextNodeField(true)
        nodeNameDialogVisible.value = false
        formEl.resetFields()
      } else {
        MsgError('节点名称已存在！')
      }
    }
  })
}

const mousedown = (event?: MouseEvent) => {
  if (!event?.shiftKey) {
    props.nodeModel.graphModel.clearSelectElements()
  }
  set(props.nodeModel, 'isSelected', !props.nodeModel.isSelected)
  set(props.nodeModel, 'isHovered', !props.nodeModel.isSelected)
  props.nodeModel.graphModel.toFront(props.nodeModel.id)
}
const showicon = ref<number | string | null>(null)
const copyNode = () => {
  props.nodeModel.graphModel.clearSelectElements()
  const cloneNode = props.nodeModel.graphModel.cloneNode(props.nodeModel.id)
  if (!cloneNode) return
  set(cloneNode, 'isSelected', true)
  set(cloneNode, 'isHovered', true)
  props.nodeModel.graphModel.toFront(cloneNode.id)
}
const deleteNode = () => {
  MsgConfirm('提示', '确定删除当前节点吗？', {
    confirmButtonText: '确定',
    confirmButtonClass: 'danger',
  }).then(() => {
    if (String(props.nodeModel.type) === WorkflowNodeType.LoopNode) {
      const next = props.nodeModel.graphModel.getNodeOutgoingNode(props.nodeModel.id)
      next.forEach((nextNode) => {
        if (String(nextNode.type) === WorkflowNodeType.LoopBodyNode) {
          props.nodeModel.graphModel.deleteNode(nextNode.id)
        }
      })
    }
    props.nodeModel.graphModel.deleteNode(props.nodeModel.id)
  })
  props.nodeModel.graphModel.eventCenter.emit('delete_node', undefined)
}
const resizeStepContainer = (wh: ResizeSize) => {
  if (wh.height) {
    if (!props.nodeModel.virtual) {
      height.value.stepContainerHeight = wh.height
      props.nodeModel.setHeight(height.value.stepContainerHeight)
    }
  }
}

function clickNodes(nodeType: WorkflowNodeType) {
  const item = BasicComponentsNode[nodeType]
  const anchor = anchorData.value
  if (!item || !anchor) return

  const width = Number((item.properties as { width?: number }).width ?? 214)
  const nodeModel = props.nodeModel.graphModel.addNode({
    type: item.type,
    properties: item.properties,
    x: anchor.x + width / 2 + 200,
    y: anchor.y - item.height,
  })
  props.nodeModel.graphModel.addEdge({
    type: 'app-edge',
    sourceNodeId: props.nodeModel.id,
    sourceAnchorId: anchor.id,
    targetNodeId: nodeModel.id,
    targetAnchorId: nodeModel.id + '_left',
  })

  closeNodeMenu()
}
const enable_exception = computed({
  set: (v) => {
    set(props.nodeModel.properties, 'enableException', v)
  },
  get: () => {
    if (props.nodeModel.properties.enableException !== undefined) {
      return props.nodeModel.properties.enableException
    }
    set(props.nodeModel.properties, 'enableException', false)
    return false
  },
})
const nodeFields = computed(() => {
  if (nodeProperties.value.config?.fields) {
    const fields = nodeProperties.value.config.fields.map((field) => {
      return {
        label: field.label,
        value: field.value,
        globeLabel: `{{${props.nodeModel.properties.stepName}.${field.value}}}`,
        globeValue: `{{context['${props.nodeModel.id}'].${field.value}}}`,
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
      globeLabel: `{{${props.nodeModel.properties.stepName}.exception_message}}`,
      globeValue: `{{context['${props.nodeModel.id}'].exception_message}}`,
    },
  ]
})
watch(enable_exception, () => {
  props.nodeModel.graphModel.eventCenter.emit(
    'delete_edge',
    props.nodeModel.outgoing.edges
      .filter((item) => item.sourceAnchorId === `${props.nodeModel.id}_exception_right`)
      .map((item) => item.id),
  )
})

function showOperate(type: string) {
  return ![
    WorkflowNodeType.Start,
    WorkflowNodeType.Base,
    WorkflowNodeType.KnowledgeBase,
    WorkflowNodeType.LoopStartNode.toString(),
    WorkflowNodeType.ToolBaseNode,
    WorkflowNodeType.ToolStartNode,
  ].includes(type)
}

function showConditionOperate(type: string) {
  return (
    ![
      WorkflowNodeType.Start,
      WorkflowNodeType.Base,
      WorkflowNodeType.ToolBaseNode,
      WorkflowNodeType.ToolStartNode,
      WorkflowNodeType.KnowledgeBase,
      WorkflowNodeType.LoopStartNode.toString(),
      WorkflowNodeType.DataSourceLocalNode,
      WorkflowNodeType.DataSourceWebNode,
    ].includes(type) && nodeProperties.value.kind != WorkflowKind.DataSource
  )
}
const openNodeMenu = (anchorValue: Model.AnchorConfig) => {
  showAnchor.value = true
  anchorData.value = anchorValue
}
const closeNodeMenu = () => {
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
  props.nodeModel.setSelected(false)
  currentKeyWord.value = false
}
/**
 * 定位时触发
 * @param kw
 */
const focusOn = () => {
  props.nodeModel.setSelected(true)
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
  set(props.nodeModel, 'openNodeMenu', (anchor: Model.AnchorConfig) => {
    showAnchor.value ? closeNodeMenu() : openNodeMenu(anchor)
  })
  set(props.nodeModel, 'selectOn', selectOn)
  set(props.nodeModel, 'focusOn', focusOn)
  set(props.nodeModel, 'clearSelectOn', clearSelectOn)
})
</script>
<template>
  <div class="workflow-node-container relative overflow-visible p-4" @mousedown="mousedown">
    <div
      class="step-container overflow-visible rounded-lg border-2 border-white bg-white p-4"
      :class="{ isSelected: props.nodeModel.isSelected, error: node_status !== 200 }"
    >
      <div v-resize="resizeStepContainer">
        <div class="flex-between">
          <div
            class="flex w-[69%] items-center"
            @dragstart.prevent
            @drag.prevent
            @dragover.prevent
            @dragend.prevent
          >
            <component
              :is="iconComponent(`${nodeModel.type}-icon`)"
              class="mr-2"
              :size="24"
              :item="nodeModel?.properties.node_data"
              style="--el-avatar-border-radius: 6px"
            />
            <h4
              class="truncate break-all"
              :title="String(nodeModel.properties.stepName ?? '')"
              v-html="highlightedStepName(String(nodeModel.properties.stepName ?? ''))"
            ></h4>
          </div>

          <div @mousemove.stop @mousedown.stop @keydown.stop @click.stop>
            <el-button text @click="showNode = !showNode">
              <MkIcon
                :icon="ArrowDownBold"
                class="text-N600 transition-transform"
                :class="showNode ? 'rotate-180' : ''"
              />
            </el-button>
            <MkDropdown
              v-if="showConditionOperate(String(nodeModel.type))"
              :teleported="false"
              trigger="click"
              placement="bottom-start"
            >
              <el-button text>
                <span>条件</span>
              </el-button>
              <template #dropdown>
                <div class="w-[280px] px-4 py-3">
                  <h5>执行条件</h5>
                  <p class="mt-2 text-N600">
                    <span>前置</span>
                    <el-select v-model="condition" class="mx-2 w-[60px]" size="small">
                      <el-option label="所有" value="AND" />
                      <el-option label="任一" value="OR" />
                    </el-select>
                    <span>连线节点执行完，执行当前节点</span>
                  </p>
                </div>
              </template>
            </MkDropdown>
            <MkDropdown
              v-if="showOperate(String(nodeModel.type))"
              :teleported="false"
              trigger="click"
            >
              <el-button text>
                <MkIcon name="icon_more_outlined" class="text-N600" />
              </el-button>
              <template #dropdown>
                <MkDropdownMenu class="min-w-36">
                  <MkDropdownItem class="p-2" @click="renameNode">
                    <template #icon><MkIcon name="icon_edit_outlined" /></template>
                    重命名
                  </MkDropdownItem>
                  <MkDropdownItem class="p-2" @click="copyNode">
                    <template #icon><MkIcon name="icon_copy_outlined" /></template>
                    复制
                  </MkDropdownItem>
                  <template
                    v-if="
                      !(
                        (String(nodeModel.type) == WorkflowNodeType.ToolLib &&
                          nodeProperties.kind == WorkflowKind.DataSource) ||
                        String(nodeModel.type) == WorkflowNodeType.DataSourceLocalNode ||
                        String(nodeModel.type) == WorkflowNodeType.DataSourceWebNode
                      )
                    "
                  >
                    <div class="flex-between p-2" @click.stop>
                      <MkIcon :icon="CircleCheck" class="text-N600" />
                      <span class="mr-4">启用状态</span>
                      <el-switch v-model="nodeEnabled" size="small" />
                    </div>
                  </template>

                  <MkDropdownItem class="border-t border-N300 p-2" @click="deleteNode">
                    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                    删除
                  </MkDropdownItem>
                  <div v-if="sourceName" class="border-t border-N300 p-2" @click.stop>
                    <div class="text-sm text-N600">来源</div>
                    <div class="mt-1 break-all text-N600">{{ sourceName }}</div>
                  </div>
                </MkDropdownMenu>
              </template>
            </MkDropdown>
          </div>
        </div>
        <el-collapse-transition>
          <div v-show="showNode" class="mt-4" @mousedown.stop @keydown.stop @click.stop>
            <el-alert
              v-if="nodeDisabled"
              class="mb-4"
              title="该节点已被禁用"
              type="error"
              show-icon
              :closable="false"
            />
            <el-alert
              v-if="node_status != 200"
              class="mb-4"
              :title="
                String(props.nodeModel.type) === WorkflowNodeType.Application
                  ? '该智能体不可用'
                  : '该工具不可用'
              "
              type="error"
              show-icon
              :closable="false"
            />
            <slot />
            <template v-if="nodeFields.length > 0">
              <div class="flex-between">
                <h5 class="my-2">
                  {{ output_title }}
                </h5>
                <div v-if="exceptionNodeList.includes(String(nodeModel.type))" class="text-right">
                  <span class="mr-2 mt-2 text-N600">异常捕获</span>
                  <el-switch v-model="enable_exception" size="small" />
                </div>
              </div>
              <div class="rounded-md bg-N100 px-3 py-1 text-N600">
                <template v-for="(item, index) in nodeFields" :key="index">
                  <div
                    class="flex-between my-2"
                    @mouseenter="showicon = index"
                    @mouseleave="showicon = null"
                  >
                    <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>
                    <el-tooltip
                      effect="dark"
                      content="复制参数"
                      placement="top"
                      v-if="showicon === index"
                    >
                      <el-button class="p-0!" link @click="copyText(item.globeLabel)">
                        <MkIcon name="icon_copy_outlined" />
                      </el-button>
                    </el-tooltip>
                  </div>
                </template>
              </div>

              <div v-if="enable_exception" class="mt-2 rounded-md bg-N100 px-3 py-1 text-N600">
                <template v-for="(item, index) in abnormalNodeFields" :key="index">
                  <div
                    class="flex-between my-2"
                    @mouseenter="showicon = 'abnormal' + index"
                    @mouseleave="showicon = null"
                  >
                    <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>
                    <el-tooltip
                      effect="dark"
                      content="复制参数"
                      placement="top"
                      v-if="showicon === 'abnormal' + index"
                    >
                      <el-button class="p-0!" link @click="copyText(item.globeLabel)">
                        <MkIcon name="icon_copy_outlined" />
                      </el-button>
                    </el-tooltip>
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
        class="absolute"
        @mousemove.stop
        @mousedown.stop
        @click.stop
        @wheel="handleNodeWheel"
        style="left: 100%; transform: translate(0, -50%)"
        :style="dropdownMenuStyle"
        @select="clickNodes"
      />
    </el-collapse-transition>

    <MkDialog v-model="nodeNameDialogVisible" title="节点名称" append-to-body @submit.prevent>
      <el-form ref="titleFormRef" :model="form" label-position="top">
        <el-form-item
          prop="title"
          :rules="[
            {
              required: true,
              message: '请输入',
              trigger: 'blur',
            },
          ]"
        >
          <el-input v-model="form.title" @blur="form.title = form.title.trim()" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click.prevent="nodeNameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="editName(titleFormRef)">保存</el-button>
      </template>
    </MkDialog>
  </div>
</template>
<style lang="scss" scoped>
.workflow-node-container {
  .step-container {
    box-sizing: border-box;
    box-shadow: 0 2px 4px 0 rgb(var(--mk-N900-rgb) / 12%);

    &:hover {
      box-shadow: 0 6px 24px 0 rgb(var(--mk-N900-rgb) / 8%);
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
