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
import MenuItem from './MenuItem.vue'

const topMenuList = computed(() => {
  return getChildRouteListByPathAndName('/', 'home')
})
</script>
<style lang="scss" scope>

</style>
