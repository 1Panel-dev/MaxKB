<template>
  <div v-if="!menu.meta || !menu.meta.hidden" class="sidebar-item">
    <el-menu-item ref="subMenu" :index="menu.path" popper-class="sidebar-popper">
      <template #title>
        <AppIcon v-if="menu.meta && menu.meta.icon" :iconName="menu.meta.icon" />
        <span v-if="menu.meta && menu.meta.title">{{ menu.meta.title }}</span>
      </template>
    </el-menu-item>
  </div>
</template>

<script setup lang="ts">
import { type RouteRecordRaw } from 'vue-router'

defineProps<{
  menu: RouteRecordRaw
}>()
</script>

<style scoped lang="scss">
.sidebar-item {
  .el-menu-item {
    padding-left: 30px !important;
    font-weight: 500;
  }

  .el-menu-item.is-active {
    color: var(--el-menu-active-color);
    background: var(--el-color-primary-light-9);
  }
}
</style>
