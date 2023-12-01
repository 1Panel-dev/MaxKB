<template>
  <div v-if="!menu.meta || !menu.meta.hidden" class="sidebar-item">
    <el-menu-item ref="subMenu" :index="menu.path" popper-class="sidebar-popper">
      <template #title>
        <AppIcon v-if="menu.meta && menu.meta.icon" :iconName="menuIcon" class="sidebar-icon" />
        <span v-if="menu.meta && menu.meta.title">{{ menu.meta.title }}</span>
      </template>
    </el-menu-item>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { type RouteRecordRaw } from 'vue-router'

const props = defineProps<{
  menu: RouteRecordRaw
  activeMenu: any
}>()
const menuIcon = computed(() => {
  if (props.activeMenu === props.menu.path) {
    return props.menu.meta?.iconActive || props.menu?.meta?.icon
  } else {
    return props.menu?.meta?.icon
  }
})
</script>

<style scoped lang="scss">
.sidebar-item {
  .sidebar-icon {
    font-size: 20px;
    margin-top: -2px;
  }
  .el-menu-item {
    padding: 13px 12px 13px 16px !important;
    font-weight: 500;
    border-radius: 4px;
    &:hover {
      background: none;
      color: var(--el-menu-active-color);
    }
  }

  .el-menu-item.is-active {
    color: var(--el-menu-active-color);
    background: var(--el-color-primary-light-9);
  }
}
</style>
