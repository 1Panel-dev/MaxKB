<template>
  <el-card shadow="always">
    <div class="card-add">
      <AppIcon :iconName="icon" class="add-icon" />
      <span class="ml-10">{{ title }}</span>
    </div>
  </el-card>
</template>
<script setup lang="ts">
defineOptions({ name: 'CardAdd' })
defineProps({
  title: {
    type: String,
    default: '标题'
  },
  icon: {
    type: String,
    default: 'CirclePlusFilled'
  }
})
</script>
<style lang="scss" scoped>
.card-add {
  width: 100%;
  min-height: 110px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 15px;
  cursor: pointer;
  &:hover {
    color: var(--el-color-primary);
  }
  .add-icon {
    font-size: 16px;
  }
}
</style>
