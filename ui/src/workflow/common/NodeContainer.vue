<template>
  <div @mousedown="mousedown" class="workflow-node-container p-16" style="overflow: visible">
    <div
      class="step-container app-card p-16"
      :class="props.nodeModel.isSelected ? 'isSelected' : ''"
      style="overflow: visible"
    >
      <div v-resize="resizeStepContainer">
        <div class="flex-between mb-16">
          <div class="flex align-center" style="max-width: 90%">
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

        <div @mousedown.stop @keydown.stop @click.stop>
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
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { set } from 'lodash'
import { iconComponent } from '../icons/utils'
import { copyClick } from '@/utils/clipboard'
import { WorkflowType } from '@/enums/workflow'
import { MsgError, MsgConfirm } from '@/utils/message'
const height = ref<{
  stepContainerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContainerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0
})

const showEditIcon = ref(false)

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
  }
}
:deep(.el-card) {
  overflow: visible;
}
</style>
