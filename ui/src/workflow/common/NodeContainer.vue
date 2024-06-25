<template>
  <div class="workflow-node-container p-16" style="overflow: visible">
    <div
      class="step-container p-16"
      :class="props.nodeModel.isSelected ? 'isSelected' : ''"
      style="overflow: visible"
    >
      <div v-resize="resizeStepContainer">
        <div class="flex-between mb-16">
          <div class="flex align-center">
            <component :is="iconComponent(`${nodeModel.type}-icon`)" class="mr-8" :size="24" />
            <h4>{{ nodeModel.properties.stepName }}</h4>
          </div>
          <div @click.stop v-if="showOperate(nodeModel.type)">
            <el-dropdown :teleported="false" trigger="click">
              <el-button text @click.stop>
                <el-icon class="color-secondary"><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu style="min-width: 80px">
                  <el-dropdown-item class="p-8">复制</el-dropdown-item>
                  <el-dropdown-item class="border-t p-8">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div>
          <slot></slot>
          <template v-if="props.nodeModel.properties.fields?.length > 0">
            <h5 class="title-decoration-1 mb-8 mt-8">参数输出</h5>
            <template v-for="(item, index) in props.nodeModel.properties.fields" :key="index">
              <div
                class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter"
                @mouseenter="showicon = index"
                @mouseleave="showicon = null"
              >
                <span>{{ item.label }} {{ '{' + item.value + '}' }}</span>
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
import { ref } from 'vue'
import { iconComponent } from '../icons/utils'
import { copyClick } from '@/utils/clipboard'
import { WorkflowType } from '@/enums/workflow'
const height = ref<{
  stepContainerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContainerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0
})

const showicon = ref<number | null>(null)

const resizeStepContainer = (wh: any) => {
  if (wh.height) {
    height.value.stepContainerHeight = wh.height
    props.nodeModel.setHeight(height.value.stepContainerHeight)
  }
}

const props = defineProps<{
  nodeModel: any
}>()

function showOperate(type: string) {
  return type !== WorkflowType.Base && type !== WorkflowType.Start
}
</script>
<style lang="scss" scoped>
.workflow-node-container {
  .step-container {
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #fff;
    border-radius: 9px;
    border: 2px solid #ffffff !important;
    box-shadow: 0px 2px 4px 0px rgba(31, 35, 41, 0.12);
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
