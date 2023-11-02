<template>
  <div class="sidebar">
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu :default-active="activeMenu">
        <sidebar-item
          :menu="menu"
          v-hasPermission="menu.meta?.permission"
          v-for="(menu, index) in subMenuList"
          :key="index"
        >
        </sidebar-item>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { getChildRouteListByPathAndName } from '@/router/index'
import SidebarItem from './SidebarItem.vue'

const route = useRoute()
const subMenuList = computed(() => {
  return getChildRouteListByPathAndName(route.path, route.name)
})

const activeMenu = computed(() => {
  const { meta, path } = route
  if (meta.activeMenu) {
    return meta.activeMenu
  }
  return path
})
</script>

<style lang="scss">
.sidebar {
  padding: 8px;
  .el-menu {
    height: 100%;
    border: none;
  }
}
</style>
