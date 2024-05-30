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
        <p class="title">基础组件</p>
        <div class="flex p-16">
          <AppAvatar class="mr-8 mt-4" shape="square" :size="32">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>
          <div class="pre-line">
            <div>通用型</div>
            <el-text type="info" size="small">可以通过上传文件或手动录入方式构建知识库</el-text>
          </div>
        </div>
      </div>
    </el-collapse-transition>
    <div class="workflow-main">
      <workflow />
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'

import Workflow from '@/components/workflow/index.vue'

const showPopover = ref(false)

function clickoutside() {
  showPopover.value = false
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
    position: absolute;
    top: 110px;
    right: 24px;
    z-index: 99;
    width: 240px;
    box-shadow: 0px 4px 8px 0px #1f23291a;
    background: #ffffff;
    border-radius: 4px;

    .title {
      font-size: 14px;
      font-weight: 500;
      padding: 8px 12px 0;
    }
  }
}
</style>
