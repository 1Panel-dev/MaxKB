·
<template>
  <div class="app-top-bar-container border-b flex-center">
    <div class="logo mt-4">
      <LogoFull />
    </div>
    <el-divider direction="vertical" class="ml-24 mr-24" />
    <Workspace />
    <div class="flex-between w-full">
      <div></div>
      <TopMenu></TopMenu>
      <TopAbout></TopAbout>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import TopMenu from './top-menu/index.vue'
import Avatar from './avatar/index.vue'
import TopAbout from './top-about/index.vue'
import Workspace from './workspace/index.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}
</style>
