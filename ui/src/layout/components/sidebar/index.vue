<template>
  <div class="sidebar-container">
    <div v-if="showBreadcrumb">
      <AppBreadcrumb />
    </div>
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu :default-active="activeMenu" router>
        <sidebar-item
          v-hasPermission="menu.meta?.permission"
          v-for="(menu, index) in subMenuList"
          :key="index"
          :menu="menu"
          :activeMenu="activeMenu"
        >
        </sidebar-item>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getChildRouteListByPathAndName } from '@/router/index'
import SidebarItem from './SidebarItem.vue'
import AppBreadcrumb from './../breadcrumb/index.vue'

const route = useRoute()

const showBreadcrumb = computed(() => {
  const { meta } = route as any
  return meta?.breadcrumb
})

const subMenuList = computed(() => {
  const { meta } = route
  return getChildRouteListByPathAndName(meta.parentPath, meta.parentName)
})

const activeMenu = computed(() => {
  const { path, meta } = route
  return meta.active || path
})
</script>

<style lang="scss" scoped>
.sidebar-container {
  padding: 8px;
  height: 100%;
}
</style>

<style lang="scss">
.sidebar-container {
  .el-menu {
    height: 100%;
    border: none;
    background: none;
    max-height: calc(100vh - 100px);
  }
}
</style>
