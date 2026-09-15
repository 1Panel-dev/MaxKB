<script setup lang="ts">
import { ref } from 'vue'

defineOptions({ name: 'UpdateDescriptionDialog' })

const visible = ref(false)
const description = ref('')

function open(content: string) {
  description.value = content
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" class="workflow-version-description-dialog" title="更新说明" width="600" align-center @closed="description = ''">
    <p class="whitespace-pre-wrap break-words leading-[30px]">{{ description || '暂无更新说明' }}</p>
  </MkDialog>
</template>

<style scoped>
/* 更新说明按内容撑开，长文本由 Dialog 的滚动区承接。 */
:global(.workflow-version-description-dialog .el-dialog__body > .el-scrollbar),
:global(.workflow-version-description-dialog .el-dialog__body > .el-scrollbar > .el-scrollbar__wrap) {
  height: auto;
}
</style>
