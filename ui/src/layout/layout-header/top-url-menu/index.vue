<template>
  <el-tooltip
    effect="dark"
    :content="$t('layout.github')"
    placement="top"
    v-if="user.themeInfo?.showProject"
  >
    <AppIcon
      iconName="app-github"
      class="cursor color-secondary mr-8 ml-8"
      style="font-size: 20px"
      @click="toUrl(user.themeInfo?.projectUrl)"
    ></AppIcon>
  </el-tooltip>
  <el-tooltip
    effect="dark"
    :content="$t('layout.wiki')"
    placement="top"
    v-if="user.themeInfo?.showUserManual"
  >
    <AppIcon
      iconName="app-reading"
      class="cursor color-secondary mr-8 ml-8"
      style="font-size: 20px"
      @click="toUrl(user.themeInfo?.userManualUrl)"
    ></AppIcon>
  </el-tooltip>
  <el-tooltip
    effect="dark"
    :content="$t('layout.forum')"
    placement="top"
    v-if="user.themeInfo?.showForum"
  >
    <AppIcon
      iconName="app-help"
      class="cursor color-secondary mr-16 ml-8"
      style="font-size: 20px"
      @click="toUrl(user.themeInfo?.forumUrl)"
    ></AppIcon>
  </el-tooltip>
</template>
<script setup lang="ts">
import useStore from '@/stores'
const { user } = useStore()
function toUrl(url: string) {
  window.open(url, '_blank')
}
</script>
