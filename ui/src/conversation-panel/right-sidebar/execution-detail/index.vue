<template>
  <!-- 右侧内容区:执行详情。数据来自 view 层(消息区点击「执行详情」写入) -->
  <div class="execution-detail-panel">
    <div class="execution-detail-panel__header">
      <span>执行详情</span>
      <!-- 关闭执行详情 -->
      <button type="button" class="execution-detail-panel__close" @click="closeRightSide()">
        <MkIcon :icon="Close" :size="16" />
      </button>
    </div>
    <div class="execution-detail-panel__body">
      <ExecutionDetailContent
        v-if="detail && detail.length"
        :detail="detail"
        :workflow-mode="workflowMode"
      />
      <el-empty v-else description="暂无执行详情" :image-size="80" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Close } from '@element-plus/icons-vue'
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import { useExecutionDetailStore } from './index'

withDefaults(defineProps<{ workflowMode?: WorkflowMode }>(), {
  workflowMode: WorkflowMode.Application,
})

const { detail, closeRightSide } = useExecutionDetailStore()
</script>

<style scoped lang="scss">
.execution-detail-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.execution-detail-panel__header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.execution-detail-panel__close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--el-text-color-secondary, #909399);
  cursor: pointer;
}
.execution-detail-panel__close:hover {
  background: rgba(0, 0, 0, 0.05);
}
.execution-detail-panel__body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px;
}
</style>
