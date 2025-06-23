<template>
  <div>
    <el-tooltip
      effect="dark"
      :content="$t('layout.github')"
      placement="top"
      v-if="theme.themeInfo?.showProject"
    >
      <AppIcon
        iconName="app-github"
        class="cursor color-secondary mr-8 ml-8"
        style="font-size: 20px"
        @click="toUrl(theme.themeInfo?.projectUrl)"
      ></AppIcon>
    </el-tooltip>
    <el-tooltip
      effect="dark"
      :content="$t('layout.wiki')"
      placement="top"
      v-if="theme.themeInfo?.showUserManual"
    >
      <AppIcon
        iconName="app-user-manual"
        class="cursor color-secondary mr-8 ml-8"
        style="font-size: 20px"
        @click="toUrl(theme.themeInfo?.userManualUrl)"
      ></AppIcon>
    </el-tooltip>
    <el-tooltip
      effect="dark"
      :content="$t('layout.forum')"
      placement="top"
      v-if="theme.themeInfo?.showForum"
    >
      <AppIcon
        iconName="app-help"
        class="cursor color-secondary mr-8 ml-8"
        style="font-size: 20px"
        @click="toUrl(theme.themeInfo?.forumUrl)"
      ></AppIcon>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
import useStore from '@/stores'
const { theme } = useStore()
function toUrl(url: string) {
  window.open(url, '_blank')
}
</script>
