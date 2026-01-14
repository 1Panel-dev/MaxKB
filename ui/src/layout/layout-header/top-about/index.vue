<template>
  <div class="flex align-center">
    <el-button
      round
      @click="toUrl('https://maxkb.cn/pricing.html')"
      class="pricing-button mr-8"
      v-hasPermission="EditionConst.IS_CE"
    >
      <AppIcon iconName="app-pricing" class="mr-8"></AppIcon>
      {{ $t('common.upgrade') }}
    </el-button>
    <el-tooltip effect="dark" :content="$t('layout.trigger', '触发器')" placement="top" v-if="true">
      <AppIcon
        iconName="app-trigger"
        class="cursor color-secondary mr-8 ml-8"
        style="font-size: 20px"
        @click=""
      ></AppIcon>
    </el-tooltip>
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
import { EditionConst, RoleConst } from '@/utils/permission/data'
const { theme, user } = useStore()

function toUrl(url: string) {
  window.open(url, '_blank')
}
</script>
<style scoped lang="scss">
.pricing-button {
  background: linear-gradient(90deg, #3370ff 0%, #7f3bf5 100%);
  color: #ffffff;
}
</style>
