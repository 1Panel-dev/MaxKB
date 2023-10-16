<template>
  <div class="top-bar-container flex-between">
    <div class="flex-center h-full">
      <div class="app-title-container flex-center">
        <div class="app-title-icon"></div>
        <div class="app-title-text ml-1">{{ defaultTitle }}</div>
      </div>
      <el-divider direction="vertical" class="line" />
      <TopMenu></TopMenu>
    </div>
    <div class="avatar">
      <Avatar></Avatar>
    </div>
  </div>
</template>
<script setup lang="ts">
import TopMenu from './top-menu/index.vue'
import Avatar from './avatar/index.vue'
const defaultTitle = import.meta.env.VITE_APP_TITLE
</script>
<style lang="scss">
.top-bar-container {
  border-bottom: 1px solid var(--el-border-color);
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);

  .app-title-container {
    margin-right: 30px;
    .app-title-icon {
      background-image: url('@/assets/logo.png');
      background-size: 100% 100%;
      width: 40px;
      height: 40px;
    }

    .app-title-text {
      color: var(--el-color-primary);
      font-size: 20px;
      font-weight: 600;
    }
  }
  .line {
    height: 2em;
  }
}
</style>
