<template>
  <div class="application-workflow">
    <div class="header border-b flex-between p-16-24">
      <div class="flex align-center">
        <back-button to="-1"></back-button>
        <h4>创建应用</h4>
      </div>
      <div>
        <el-button icon="Plus" @click="showPopover = !showPopover" v-click-outside="clickoutside">
          添加组件
        </el-button>
        <el-button> 调试 </el-button>
        <el-button type="primary"> 保存 </el-button>
      </div>
    </div>
    <!-- 下拉框 -->
    <el-collapse-transition>
      <div v-show="showPopover" class="workflow-dropdown-menu border">
        <h5 class="title">基础组件</h5>
        <template v-for="(item, index) in shapeList" :key="index">
          <div class="workflow-dropdown-item cursor flex p-8-12" @mousedown="onmousedown(item)">
            <component :is="iconComponent(item.icon)" class="mr-8 mt-4" />
            <div class="pre-line">
              <div>{{ item.label }}</div>
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
type ShapeItem = {
  type?: string
  text?: string
  icon?: string
  label?: string
  className?: string
  disabled?: boolean
  properties?: Record<string, any>
  callback?: (lf: LogicFlow, container: HTMLElement) => void
}

const workflowRef = ref()

const showPopover = ref(false)

function clickoutside() {
  showPopover.value = false
}

function onmousedown(item: ShapeItem) {
  workflowRef.value?.onmousedown(item)
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
    width: 100vw;
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
    border-radius: 4px;

    .title {
      padding: 8px 12px 4px;
    }
    .workflow-dropdown-item {
      &:hover {
        background: var(--app-text-color-light-1);
      }
    }
  }
}
</style>
