<template>
  <LayoutContainer header="创建应用" back-to="-1">
    <el-row>
      <el-col :span="10" class="p-24"> </el-col>
      <el-col :span="14" class="p-24 border-l">
        <h4 class="title-decoration-1 mb-8">调试预览</h4>
        <div class="dialog-height">
          <AiDialog></AiDialog>
        </div>
      </el-col>
    </el-row>
  </LayoutContainer>
</template>
<script setup lang="ts">
import AiDialog from '@/components/ai-dialog/index.vue'
</script>
<style lang="scss" scoped>
.dialog-height {
  height: calc(var(--app-main-height) - 75px);
}
</style>
