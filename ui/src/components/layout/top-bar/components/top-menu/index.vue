<template>
  <div class="top-menu-container flex h-full">
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
import MenuItem from '@/components/layout/top-bar/components/top-menu/MenuItem.vue'
const topMenuList = computed(() => {
  return getChildRouteListByPathAndName('/', 'home')
})
</script>
<style lang="scss" scope>
.top-menu-container {
  align-items: center;
  margin-bottom: -1px;
}
</style>
