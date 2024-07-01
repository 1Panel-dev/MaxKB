<template>
  <div class="flex align-center mt-16" v-if="!isWorkFlow(props.type)">
    <span class="mr-4 color-secondary">知识来源</span>
    <el-divider direction="vertical" />
    <el-button type="primary" class="mr-8" link @click="openParagraph(data)">
      <AppIcon iconName="app-reference-outlined" class="mr-4"></AppIcon>
      引用分段 {{ data.paragraph_list?.length || 0 }}</el-button
    >
  </div>
  <div class="mt-8" v-if="!isWorkFlow(props.type)">
    <el-space wrap>
      <el-button
        v-for="(dataset, index) in data.dataset_list"
        :key="index"
        size="small"
        class="source_dataset-button"
        @click="openParagraph(data, dataset.id)"
        >{{ dataset.name }}</el-button
      >
    </el-space>
  </div>

  <div class="border-t color-secondary flex-between mt-12" style="padding-top: 12px">
    <div>
      <span class="mr-8"> 消耗 tokens: {{ data?.message_tokens + data?.answer_tokens }} </span>
      <span> 耗时: {{ data?.run_time?.toFixed(2) }} s</span>
    </div>
    <el-button
      v-if="isWorkFlow(props.type)"
      type="primary"
      link
      @click="openExecutionDetail(data.execution_details)"
    >
      <el-icon class="mr-4"><Document /></el-icon>
      执行详情</el-button
    >
  </div>
  <!-- 知识库引用 dialog -->
  <ParagraphSourceDialog ref="ParagraphSourceDialogRef" />
  <!-- 执行详情 dialog -->
  <ExecutionDetailDialog ref="ExecutionDetailDialogRef" />
</template>
<script setup lang="ts">
import { ref } from 'vue'
import ParagraphSourceDialog from './ParagraphSourceDialog.vue'
import ExecutionDetailDialog from './ExecutionDetailDialog.vue'
import { isWorkFlow } from '@/utils/application'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  type: {
    type: String,
    default: ''
  }
})

const ParagraphSourceDialogRef = ref()
const ExecutionDetailDialogRef = ref()
function openParagraph(row: any, id?: string) {
  ParagraphSourceDialogRef.value.open(row, id)
}
function openExecutionDetail(row: any) {
  ExecutionDetailDialogRef.value.open(row)
}
</script>
<style lang="scss" scoped>
.source_dataset-button {
  background: var(--app-text-color-light-1);
  border: 1px solid #ffffff;
  &:hover {
    border: 1px solid var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    color: var(--el-text-color-primary);
  }
}
</style>
