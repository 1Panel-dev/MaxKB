·
<template>
  <div class="top-bar-container border-b flex-between">
    <div class="flex-center h-full">
      <div class="app-title-container cursor" @click="router.push('/')">
        <div class="logo flex-center">
          <LogoFull />
        </div>
      </div>
      <TopMenu></TopMenu>
    </div>
    <div class="flex-center avatar">
      <el-button
        v-if="!user.isEnterprise()"
        link
        type="primary"
        @click="toUrl('https://maxkb.cn/pricing.html')"
        class="mr-8"
      >
        <AppIcon iconName="app-pricing" class="mr-8" style="font-size: 20px"></AppIcon>
        购买专业版
      </el-button>
      <el-tooltip effect="dark" :content="$t('layout.topbar.github')" placement="top">
        <AppIcon
          iconName="app-github"
          class="cursor color-secondary mr-8 ml-8"
          style="font-size: 20px"
          @click="toUrl('https://github.com/1Panel-dev/MaxKB')"
        ></AppIcon>
      </el-tooltip>
      <el-tooltip effect="dark" :content="$t('layout.topbar.wiki')" placement="top">
        <AppIcon
          iconName="app-reading"
          class="cursor color-secondary mr-8 ml-8"
          style="font-size: 20px"
          @click="toUrl('https://maxkb.cn/docs/')"
        ></AppIcon>
      </el-tooltip>
      <el-tooltip effect="dark" :content="$t('layout.topbar.forum')" placement="top">
        <AppIcon
          iconName="app-help"
          class="cursor color-secondary mr-16 ml-8"
          style="font-size: 20px"
          @click="toUrl('https://bbs.fit2cloud.com/c/mk/11')"
        ></AppIcon>
      </el-tooltip>
      <el-dropdown v-if="false" trigger="click" type="primary">
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="(lang, index) in langList"
              :key="index"
              :value="lang.value"
              @click="changeLang(lang.value)"
              >{{ lang.label }}</el-dropdown-item
            >
          </el-dropdown-menu>
        </template>
        <AppIcon
          iconName="app-translate"
          class="cursor color-secondary mr-16 ml-8"
          style="font-size: 20px"
        >
        </AppIcon>
      </el-dropdown>
      <Avatar></Avatar>
    </div>
  </div>
</template>
<script setup lang="ts">
import TopMenu from './top-menu/index.vue'
import Avatar from './avatar/index.vue'
import { useRouter } from 'vue-router'
import { langList } from '@/locales/index'
import { useLocale } from '@/locales/useLocale'

import useStore from '@/stores'
const { user } = useStore()
const router = useRouter()

const { changeLocale } = useLocale()
const changeLang = (lang: string) => {
  changeLocale(lang)
}
function toUrl(url: string) {
  window.open(url, '_blank')
}
</script>
<style lang="scss">
.top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);

  .app-title-container {
    margin-right: 45px;
  }

  .line {
    height: 2em;
  }
}
</style>
