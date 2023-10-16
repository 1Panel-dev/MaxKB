<template>
  <div v-if="!menu.meta || !menu.meta.hidden">
    <el-menu-item ref="subMenu" :index="menu.path" popper-class="sidebar-popper">
      <template #title>
        <AppIcon v-if="menu.meta && menu.meta.icon" :iconName="menu.meta.icon" />
        <span v-if="menu.meta && menu.meta.title">{{ menu.meta.title }}</span>
      </template>
    </el-menu-item>
  </div>
</template>

<script setup lang="ts">
import { RouteRecordRaw } from 'vue-router'

defineProps<{
  menu: RouteRecordRaw
}>()
</script>

<style scoped lang="scss"></style>
