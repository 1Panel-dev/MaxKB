<template>
  <div @mousedown="mousedown" class="workflow-node-container p-16" style="overflow: visible">
    <div
      class="step-container app-card p-16"
      :class="{ isSelected: props.nodeModel.isSelected, error: node_status !== 200 }"
      style="overflow: visible"
    >
      <div v-resize="resizeStepContainer">
        <div class="flex-between">
          <div
            class="flex align-center"
            :style="{ maxWidth: node_status == 200 ? 'calc(100% - 55px)' : 'calc(100% - 85px)' }"
          >
            <component :is="iconComponent(`${nodeModel.type}-icon`)" class="mr-8" :size="24" />
            <h4 v-if="showOperate(nodeModel.type)" style="max-width: 90%">
              <ReadWrite
                @mousemove.stop
                @mousedown.stop
                @keydown.stop
                @click.stop
                @change="editName"
                :data="nodeModel.properties.stepName"
                trigger="dblclick"
              />
            </h4>
            <h4 v-else>{{ nodeModel.properties.stepName }}</h4>
          </div>

          <div
            @mousemove.stop
            @mousedown.stop
            @keydown.stop
            @click.stop
            v-if="showOperate(nodeModel.type)"
          >
            <el-button text @click="showNode = !showNode" class="mr-4">
              <el-icon class="arrow-icon" :class="showNode ? 'rotate-180' : ''"
                ><ArrowDownBold />
              </el-icon>
            </el-button>
            <el-dropdown :teleported="false" trigger="click">
              <el-button text>
                <el-icon class="color-secondary"><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu style="min-width: 80px">
                  <el-dropdown-item @click="copyNode" class="p-8">复制</el-dropdown-item>
                  <el-dropdown-item @click="deleteNode" class="border-t p-8">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        <el-collapse-transition>
          <div @mousedown.stop @keydown.stop @click.stop v-if="showNode" class="mt-16">
            <el-alert
              v-if="node_status != 200"
              class="mb-16"
              title="该函数不可用"
              type="error"
              show-icon
              :closable="false"
            />
            <slot></slot>
            <template v-if="nodeFields.length > 0">
              <h5 class="title-decoration-1 mb-8 mt-8">参数输出</h5>
              <template v-for="(item, index) in nodeFields" :key="index">
                <div
                  class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter"
                  @mouseenter="showicon = index"
                  @mouseleave="showicon = null"
                >
                  <span style="max-width: 92%">{{ item.label }} {{ '{' + item.value + '}' }}</span>
                  <el-tooltip
                    effect="dark"
                    content="复制参数"
                    placement="top"
                    v-if="showicon === index"
                  >
                    <el-button link @click="copyClick(item.globeLabel)" style="padding: 0">
                      <AppIcon iconName="app-copy"></AppIcon>
                    </el-button>
                  </el-tooltip>
                </div>
              </template>
            </template>
          </div>
        </el-collapse-transition>
      </div>
    </div>

    <el-collapse-transition>
      <DropdownMenu
        v-if="showAnchor"
        @mousemove.stop
        @mousedown.stop
        @keydown.stop
        @click.stop
        @wheel.stop
        :show="showAnchor"
        :id="id"
        style="left: 100%; top: 50%; transform: translate(0, -50%)"
        @clickNodes="clickNodes"
      />
    </el-collapse-transition>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { app } from '@/main'
import DropdownMenu from '@/views/application-workflow/component/DropdownMenu.vue'
import { set } from 'lodash'
import { iconComponent } from '../icons/utils'
import { copyClick } from '@/utils/clipboard'
import { WorkflowType } from '@/enums/workflow'
import { MsgError, MsgConfirm } from '@/utils/message'

const {
  params: { id }
} = app.config.globalProperties.$route as any

const height = ref<{
  stepContainerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContainerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0
})
const showAnchor = ref<boolean>(false)
const anchorData = ref<any>()
const showNode = ref<boolean>(true)
const node_status = computed(() => {
  if (props.nodeModel.properties.status) {
    return props.nodeModel.properties.status
  }
  return 200
})
function editName(val: string) {
  if (val.trim() && val.trim() !== props.nodeModel.properties.stepName) {
    if (
      !props.nodeModel.graphModel.nodes?.some(
        (node: any) => node.properties.stepName === val.trim()
      )
    ) {
      set(props.nodeModel.properties, 'stepName', val.trim())
    } else {
      MsgError('节点名称已存在！')
    }
  }
}
const mousedown = () => {
  props.nodeModel.graphModel.clearSelectElements()
  set(props.nodeModel, 'isSelected', true)
  set(props.nodeModel, 'isHovered', true)
  props.nodeModel.graphModel.toFront(props.nodeModel.id)
}
const showicon = ref<number | null>(null)
const copyNode = () => {
  props.nodeModel.graphModel.clearSelectElements()
  const cloneNode = props.nodeModel.graphModel.cloneNode(props.nodeModel.id)
  set(cloneNode, 'isSelected', true)
  set(cloneNode, 'isHovered', true)
  props.nodeModel.graphModel.toFront(cloneNode.id)
}
const deleteNode = () => {
  MsgConfirm(`提示`, `确定删除该节点？`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  }).then(() => {
    props.nodeModel.graphModel.deleteNode(props.nodeModel.id)
  })
  props.nodeModel.graphModel.eventCenter.emit('delete_node')
}
const resizeStepContainer = (wh: any) => {
  if (wh.height) {
    if (!props.nodeModel.virtual) {
      height.value.stepContainerHeight = wh.height
      props.nodeModel.setHeight(height.value.stepContainerHeight)
    }
  }
}

function clickNodes(item: any) {
  const width = item.properties.width ? item.properties.width : 214
  const nodeModel = props.nodeModel.graphModel.addNode({
    type: item.type,
    properties: item.properties,
    x: anchorData.value?.x + width / 2 + 200,
    y: anchorData.value?.y - item.height
  })
  props.nodeModel.graphModel.addEdge({
    type: 'app-edge',
    sourceNodeId: props.nodeModel.id,
    sourceAnchorId: anchorData.value?.id,
    targetNodeId: nodeModel.id
  })

  closeNodeMenu()
}

const props = defineProps<{
  nodeModel: any
}>()
const nodeFields = computed(() => {
  if (props.nodeModel.properties.config.fields) {
    const fields = props.nodeModel.properties.config.fields?.map((field: any) => {
      return {
        label: field.label,
        value: field.value,
        globeLabel: `{{${props.nodeModel.properties.stepName}.${field.value}}}`,
        globeValue: `{{context['${props.nodeModel.id}'].${field.value}}}`
      }
    })
    return fields
  }
  return []
})

function showOperate(type: string) {
  return type !== WorkflowType.Base && type !== WorkflowType.Start
}
const openNodeMenu = (anchorValue: any) => {
  showAnchor.value = true
  anchorData.value = anchorValue
}
const closeNodeMenu = () => {
  showAnchor.value = false
  anchorData.value = undefined
}
onMounted(() => {
  set(props.nodeModel, 'openNodeMenu', (anchorData: any) => {
    showAnchor.value ? closeNodeMenu() : openNodeMenu(anchorData)
  })
})
</script>
<style lang="scss" scoped>
.workflow-node-container {
  .step-container {
    border: 2px solid #ffffff !important;
    box-sizing: border-box;
    &:hover {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
    }
    &.isSelected {
      border: 2px solid var(--el-color-primary) !important;
    }
    &.error {
      border: 1px solid #f54a45 !important;
    }
  }
  .arrow-icon {
    transition: 0.2s;
  }
}
:deep(.el-card) {
  overflow: visible;
}
</style>
