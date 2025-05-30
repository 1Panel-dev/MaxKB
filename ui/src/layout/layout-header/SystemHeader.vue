·
<template>
  <div class="app-top-bar-container border-b flex-center">
    <div class="logo mt-4">
      <LogoFull />
    </div>

    <div class="flex-between w-full">
      <h4><el-divider class="ml-16 mr-16" direction="vertical" />{{ $t('views.system.title') }}</h4>
      <div>
        <TopAbout></TopAbout>
        <span class="mr-8 lighter flex align-center"
          ><el-divider class="ml-8 mr-8" direction="vertical" />
          <el-button link @click="router.push({ path: '/' })">
            <AppIcon class="mr-8" iconName="app-wordspace" style="font-size: 16px"></AppIcon>
            {{ '返回工作空间' }}</el-button>
        </span>
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
