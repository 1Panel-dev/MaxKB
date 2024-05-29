<template>
  <div class="application-workflow">
    <div class="header border-b flex-between p-16-24">
      <div class="flex align-center">
        <back-button to="-1"></back-button>
        <h4>创建应用</h4>
      </div>
      <div>
        <el-button> 添加组件 </el-button>
        <el-button> 调试 </el-button>
        <el-button type="primary"> 保存 </el-button>
      </div>
    </div>
    <div class="workflow-main">
      <workflow />
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'

import Workflow from '@/components/workflow/index.vue'

onMounted(() => {})

onBeforeUnmount(() => {})
</script>
<style lang="scss" scoped>
.application-workflow {
  .header {
    background: #ffffff;
  }
  .workflow-main {
    width: 100vw;
    height: calc(100vh - var(--app-header-height) - 70px);
  }
}
</style>
