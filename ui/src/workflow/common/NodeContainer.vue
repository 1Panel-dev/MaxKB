<template>
  <div class="workflow-node-container p-16">
    <div class="step-container p-16">
      <div v-resize="resizeStepContainer">
        <div class="flex align-center mb-16">
          <component :is="iconComponent(`${nodeModel.type}-icon`)" class="mr-8" :size="24" />
          <h4>{{ nodeModel.properties.stepName }}</h4>
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
    box-shadow: 0px 2px 4px 0px rgba(31, 35, 41, 0.12);
    &:hover {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
    }
  }
}

.step-field {
  display: flex;
  justify-content: space-between;
  height: 24px;
  padding: 0 10px;
  font-size: 12px;
  line-height: 24px;
}

.field-type {
  color: #9f9c9f;
}
.out-step-field {
  display: flex;
  justify-content: space-between;
  height: 24px;
  padding: 0 10px;
  font-size: 12px;
  line-height: 24px;
  float: right;
}
/* 自定义锚点样式 */
.custom-anchor {
  cursor: crosshair;
  fill: #d9d9d9;
  stroke: #999;
  stroke-width: 1;
  rx: 3;
  ry: 3;
}

.custom-anchor:hover {
  fill: #ff7f0e;
  stroke: #ff7f0e;
}

.lf-node-not-allow .custom-anchor:hover {
  cursor: not-allowed;
  fill: #d9d9d9;
  stroke: #999;
}

.outgoing-anchor {
  stroke: #82b366;
}
</style>
