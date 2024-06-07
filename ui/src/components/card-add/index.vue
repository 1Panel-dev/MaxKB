<template>
  <el-card shadow="never" class="card-add">
    <div class="flex-center">
      <AppIcon iconName="Plus" class="add-icon p-8 border-r-4 layout-bg" />
      <span>{{ title }}</span>
    </div>
  </el-card>
</template>
<script setup lang="ts">
defineOptions({ name: 'CardAdd' })
defineProps({
  title: {
    type: String,
    default: '标题'
  }
})
</script>
<style lang="scss" scoped>
.card-add {
  width: 100%;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  cursor: pointer;
  min-height: var(--card-min-height);
  border: 1px dashed var(--el-border-color);
  background: #eff0f1;
  border-radius: 8px;
  box-sizing: border-box;

  .add-icon {
    font-size: 14px;
    border: 1px solid var(--app-border-color-dark);
    margin-right: 12px;
  }
  &:hover {
    color: var(--el-color-primary);
    background: #ffffff;
    border: 1px dashed var(--el-color-primary);
    .add-icon {
      background: #ffffff;
      border-color: var(--el-color-primary);
    }
  }
}
</style>
