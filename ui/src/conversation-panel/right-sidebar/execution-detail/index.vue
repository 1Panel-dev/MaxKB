<script setup lang="ts">
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import { useExecutionDetailStore } from './index'

withDefaults(defineProps<{ workflowMode?: WorkflowMode }>(), {
  workflowMode: WorkflowMode.Application,
})

const { detail, closeRightSide } = useExecutionDetailStore()
</script>

<template>
  <!-- 右侧内容区:执行详情。数据来自 view 层(消息区点击「执行详情」写入) -->
  <div class="execution-detail-panel flex-column h-full">
    <div class="flex-between shrink-0 px-6 py-4 border-b">
      <h4>执行详情</h4>
      <!-- 关闭执行详情 -->
      <el-button text @click="closeRightSide()">
        <MkIcon name="icon_close_outlined" size="18" />
      </el-button>
    </div>
    <el-scrollbar class="min-h-0 flex-1" view-class="p-6">
      <ExecutionDetailContent v-if="detail && detail.length" :detail="detail" :workflow-mode="workflowMode" />
      <el-empty v-else description="暂无执行详情" :image-size="80" />
    </el-scrollbar>
  </div>
</template>
<style scoped lang="scss"></style>
