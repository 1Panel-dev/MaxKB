<template>
  <div class="workflow-node-container p-16">
    <div class="step-container p-16">
      <div v-resize="resizeStepContainer">
        <div class="flex align-center mb-16">
          <component :is="iconComponent(`${nodeModel.type}-icon`)" class="mr-8" :size="24" />
          <h4>{{ nodeModel.properties.stepName }}</h4>
        </div>
        <div><slot></slot></div>
      </div>
      <!-- <div class="input-container" v-resize="resetInputContainer">
        <div v-for="(item, index) in nodeModel.properties.input" :key="index" class="step-field">
          <span>{{ item.key }}</span>
        </div>
      </div>
      <div class="output-container" v-resize="resetOutputContainer">
        <div
          v-for="(item, index) in nodeModel.properties.output"
          :key="index"
          class="out-step-field"
        >
          <span>{{ item.key }}</span>
        </div>
      </div> -->
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { iconComponent } from '../icons/utils'

const height = ref<{
  stepContainerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContainerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0
})

const resizeStepContainer = (wh: any) => {
  if (wh.height) {
    height.value.stepContainerHeight = wh.height
    props.nodeModel.setHeight(
      height.value.stepContainerHeight,
      height.value.inputContainerHeight,
      height.value.outputContainerHeight
    )
  }
}

const resetOutputContainer = (wh: { height: number; width: number }) => {
  if (wh.height) {
    height.value.outputContainerHeight = wh.height
    props.nodeModel.setHeight(
      height.value.stepContainerHeight,
      height.value.inputContainerHeight,
      height.value.outputContainerHeight
    )
  }
}

const resetInputContainer = (wh: { height: number; width: number }) => {
  if (wh.height) {
    height.value.inputContainerHeight = wh.height
    props.nodeModel.setHeight(
      height.value.stepContainerHeight,
      height.value.inputContainerHeight,
      height.value.outputContainerHeight
    )
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

.incomming-anchor {
  stroke: #d79b00;
}

.outgoing-anchor {
  stroke: #82b366;
}
</style>
