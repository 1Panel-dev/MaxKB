·
<template>
  <div class="app-top-bar-container border-b flex-center">
    <div class="logo mt-4">
      <LogoFull />
    </div>

    <div class="flex-between w-full align-center">
      <h4><el-divider class="ml-16 mr-16" direction="vertical" />{{ $t('views.system.title') }}</h4>
      <div class="flex align-center mr-8">
        <TopAbout class="mt-4"></TopAbout>
        <el-divider class="ml-8 mr-8" direction="vertical" />
        <el-button link @click="router.push({ path: '/' })">
          <AppIcon class="mr-8" iconName="app-wordspace" style="font-size: 16px"></AppIcon>
          {{ '返回工作空间' }}</el-button
        >
      </div>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import Avatar from './avatar/index.vue'
import TopAbout from './top-about/index.vue'
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
