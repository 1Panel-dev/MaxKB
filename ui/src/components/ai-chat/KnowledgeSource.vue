<template>
  <div class="flex align-center mt-16">
    <span class="mr-4 color-secondary">知识来源</span>
    <el-divider direction="vertical" />
    <el-button type="primary" class="mr-8" link @click="openParagraph(data)">
      <AppIcon iconName="app-reference-outlined" class="mr-4"></AppIcon>
      引用分段 {{ data.paragraph_list?.length || 0 }}</el-button
    >
  </div>
  <div class="mt-8 mb-12">
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

  <div class="border-t color-secondary" style="padding-top: 12px">
    <span class="mr-8"> 消耗 tokens: {{ data?.message_tokens + data?.answer_tokens }} </span>
    <span> 耗时: {{ data?.run_time?.toFixed(2) }} s</span>
  </div>
  <!-- 知识库引用 dialog -->
  <ParagraphSourceDialog ref="ParagraphSourceDialogRef" />
</template>
<script setup lang="ts">
import { ref } from 'vue'
import ParagraphSourceDialog from './ParagraphSourceDialog.vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})

const ParagraphSourceDialogRef = ref()
function openParagraph(row: any, id?: string) {
  ParagraphSourceDialogRef.value.open(row, id)
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
