<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <div class="empty-node-content">
        <p class="empty-text">{{ $t('workflow.nodes.emptyNode.description') }}</p>
        <p class="empty-hint">{{ $t('workflow.nodes.emptyNode.hint') }}</p>
      </div>
    </el-card>
  </NodeContainer>
</template>

<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { onMounted } from 'vue'

const props = defineProps<{ nodeModel: any }>()

const validate = () => {
  return Promise.resolve()
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>

<style lang="scss" scoped>
.empty-node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px;
  text-align: center;

  .empty-text {
    font-size: 14px;
    color: #606266;
    margin: 0 0 8px 0;
  }

  .empty-hint {
    font-size: 13px;
    color: #909399;
    margin: 0;
  }
}
</style>
