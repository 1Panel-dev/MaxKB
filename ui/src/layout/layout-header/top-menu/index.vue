<template>
  <div class="top-menu-container flex align-center h-full">
    <MenuItem
      :menu="menu"
      v-hasPermission="menu.meta?.permission"
      v-for="(menu, index) in topMenuList"
      :key="index"
    >
    </MenuItem>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { getChildRouteListByPathAndName } from '@/router/index'
import { hasPermission, set_next_route } from '@/utils/permission/index'
import MenuItem from './MenuItem.vue'

const topMenuList = computed(() => {
  const menu = getChildRouteListByPathAndName('/', 'home').filter(
    (item) =>
      item.meta?.menu &&
      (item.meta.permission ? hasPermission(item.meta.permission as any, 'OR') : true),
  )
  menu.sort(
    (a, b) =>
      (a.meta ? (a.meta.order ? (a.meta.order as number) : 1) : 1) -
      (b.meta ? (b.meta.order ? (b.meta.order as number) : 1) : 1),
  )
  return menu
})
</script>
<style lang="scss" scope>
.top-menu-container {
  line-height: var(--app-header-height);
}
</style>
