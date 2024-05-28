<template>
  <div class="container">
    <div class="step-container" :class="`step-color-${Math.ceil(Math.random() * 4)}`">
      <div v-resize="resizeStepContainer">
        <div class="step-name">{{ nodeModel.properties.stepName }}</div>
        <div style="padding: 10px"><slot></slot></div>
      </div>
      <div class="input-container" v-resize="resetInputContainer">
        <el-divider> </el-divider>
        <div v-for="item in nodeModel.properties.input" class="step-feild">
          <span>{{ item.key }}</span>
        </div>
      </div>
      <div class="outout-container" v-resize="resetOutputContainer">
        <el-divider> </el-divider>
        <div v-for="item in nodeModel.properties.output" class="out-step-feild">
          <span>{{ item.key }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
const height = ref<{
  stepContanerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContanerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0
})

const resizeStepContainer = (wh: any) => {
  if (wh.height) {
    height.value.stepContanerHeight = wh.height
    props.nodeModel.setHeight(
      height.value.stepContanerHeight,
      height.value.inputContainerHeight,
      height.value.outputContainerHeight
    )
  }
}

const resetOutputContainer = (wh: { height: number; width: number }) => {
  if (wh.height) {
    height.value.outputContainerHeight = wh.height
    props.nodeModel.setHeight(
      height.value.stepContanerHeight,
      height.value.inputContainerHeight,
      height.value.outputContainerHeight
    )
  }
}

const resetInputContainer = (wh: { height: number; width: number }) => {
  if (wh.height) {
    height.value.inputContainerHeight = wh.height
    props.nodeModel.setHeight(
      height.value.stepContanerHeight,
      height.value.inputContainerHeight,
      height.value.outputContainerHeight
    )
  }
}

const props = defineProps<{
  nodeModel: any
}>()
</script>
<style lang="scss">
.el-divider--horizontal {
  margin: 0;
}
.container {
  box-sizing: border-box;
  padding: 10px;
}
.step-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgb(0 0 0 / 30%);
}

.step-container::before {
  display: block;
  width: 100%;
  height: 8px;
  background: #d79b00;
  content: '';
}

.step-container.step-color-1::before {
  background: #9673a6;
}

.step-container.step-color-2::before {
  background: #dae8fc;
}

.step-container.step-color-3::before {
  background: #82b366;
}

.step-container.step-color-4::before {
  background: #f8cecc;
}

.step-name {
  height: 28px;
  font-size: 14px;
  line-height: 28px;
  text-align: center;
  background: #f5f5f5;
}

.step-feild {
  display: flex;
  justify-content: space-between;
  height: 24px;
  padding: 0 10px;
  font-size: 12px;
  line-height: 24px;
}

.feild-type {
  color: #9f9c9f;
}
.out-step-feild {
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
