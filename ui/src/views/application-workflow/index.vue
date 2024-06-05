<template>
  <div class="application-workflow">
    <div class="header border-b flex-between p-16-24">
      <div class="flex align-center">
        <back-button to="-1"></back-button>
        <h4>创建应用</h4>
      </div>
      <div>
        <button @click="validate">点击校验</button>
        <button @click="getGraphData">点击获取流程数据</button>
        <el-button icon="Plus" @click="showPopover = !showPopover" v-click-outside="clickoutside">
          添加组件
        </el-button>
        <el-button> 调试 </el-button>
        <el-button type="primary"> 保存 </el-button>
      </div>
    </div>
    <!-- 下拉框 -->
    <el-collapse-transition>
      <div v-show="showPopover" class="workflow-dropdown-menu border border-r-4">
        <h5 class="title">基础组件</h5>
        <template v-for="(item, index) in shapeList" :key="index">
          <div class="workflow-dropdown-item cursor flex p-8-12" @mousedown="onmousedown(item)">
            <component :is="iconComponent(item.icon)" class="mr-8 mt-4" :size="32" />
            <div class="pre-line">
              <div class="lighter">{{ item.label }}</div>
              <el-text type="info" size="small">{{ item.text }}</el-text>
            </div>
          </div>
        </template>
      </div>
    </el-collapse-transition>
    <div class="workflow-main">
      <workflow ref="workflowRef" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import Workflow from '@/components/workflow/index.vue'
import { shapeList, iconComponent } from '@/components/workflow/menu-data'

const workflowRef = ref()

const showPopover = ref(false)

function clickoutside() {
  showPopover.value = false
}

function onmousedown(item: any) {
  workflowRef.value?.onmousedown(item)
}

function validate() {
  workflowRef.value?.validate()
}
function getGraphData() {
  workflowRef.value?.getGraphData()
}

onMounted(() => {})

onBeforeUnmount(() => {})
</script>
<style lang="scss">
.application-workflow {
  .header {
    background: #ffffff;
  }
  .workflow-main {
    height: calc(100vh - var(--app-header-height) - 70px);
  }
  .workflow-dropdown-menu {
    -moz-user-select: none; /* Firefox */
    -webkit-user-select: none; /* WebKit内核 */
    -ms-user-select: none; /* IE10及以后 */
    -khtml-user-select: none; /* 早期浏览器 */
    -o-user-select: none; /* Opera */
    user-select: none; /* CSS3属性 */
    position: absolute;
    top: 110px;
    right: 24px;
    z-index: 99;
    width: 240px;
    box-shadow: 0px 4px 8px 0px var(--app-text-color-light-1);
    background: #ffffff;
    padding-bottom: 8px;

    .title {
      padding: 12px 12px 4px;
    }
    .workflow-dropdown-item {
      &:hover {
        background: var(--app-text-color-light-1);
      }
    }
  }
}
</style>
