<template>
  <div class="top-bar-container">
    <div class="app-title-container">
      <div class="app-title-icon"></div>
      <div class="app-title-text">{{ defaultTitle }}</div>
      <div class="line"></div>
    </div>
    <div class="app-top-menu-container">
      <TopMenu></TopMenu>
    </div>
    <div class="flex-auto"></div>
    <div class="avatar">
      <Avatar></Avatar>
    </div>
  </div>
</template>
<script setup lang="ts">
import TopMenu from '@/components/layout/top-bar/components/top-menu/index.vue'
import Avatar from '@/components/layout/top-bar/components/avatar/index.vue'
const defaultTitle = import.meta.env.VITE_APP_TITLE
</script>
<style lang="scss">
.top-bar-container {
  border-bottom: 1px solid rgba(229, 229, 229, 1);
  height: calc(100% - 1px);
  background-color: var(--app-header-background-color, #fff);
  width: 100vw;
  display: flex;

  .flex-auto {
    flex: 1 1 auto;
  }

  .avatar {
    height: 100%;
    width: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 10px;
  }

  .app-title-container {
    width: 200px;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;

    .app-title-icon {
      background-image: url('@/assets/logo.png');
      background-size: 100% 100%;
      width: 40px;
      height: 40px;
    }

    .app-title-text {
      color: var(--app-base-action-text-color);
      font-size: 20px;
      font-weight: 600;
      align-items: center;
    }

    .line {
      height: 60%;
      width: 1px;
      margin-left: 20px;
      background-color: rgba(229, 229, 229, 1);
    }
  }
}
</style>
