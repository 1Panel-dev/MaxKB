<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <el-row class="container w-full h-full">
        <el-col :xs="0" :sm="0" :md="10" :lg="10" :xl="10" class="left-container">
          <div class="login-image" :style="{ backgroundImage: `url(${loginImage})` }"></div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="14" :lg="14" :xl="14" class="right-container flex-center">
          <el-dropdown trigger="click" type="primary" class="lang" v-if="lang">
            <template #dropdown>
              <el-dropdown-menu class="w-180">
                <el-dropdown-item
                  v-for="(lang, index) in langList"
                  :key="index"
                  :value="lang.value"
                  @click="changeLang(lang.value)"
                  class="flex-between"
                >
                  <span :class="lang.value === user.getLanguage() ? 'primary' : ''">{{
                    lang.label
                  }}</span>

                  <el-icon
                    :class="lang.value === user.getLanguage() ? 'primary' : ''"
                    v-if="lang.value === user.getLanguage()"
                  >
                    <Check />
                  </el-icon>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
            <el-button>
              {{ currentLanguage }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
          </el-dropdown>
          <slot></slot>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { getThemeImg } from '@/utils/theme'
import useStore from '@/stores'
import { useLocalStorage } from '@vueuse/core'
import { langList, localeConfigKey, getBrowserLang } from '@/locales/index'
defineProps({
  lang: {
    type: Boolean,
    default: true,
  },
})
const { user, theme } = useStore()

const changeLang = (lang: string) => {
  useLocalStorage(localeConfigKey, getBrowserLang()).value = lang
  window.location.reload()
}

const currentLanguage = computed(() => {
  return langList.value?.filter((v: any) => v.value === user.getLanguage())?.[0]?.label
})

const fileURL = computed(() => {
  if (theme.themeInfo?.loginImage) {
    if (typeof theme.themeInfo?.loginImage === 'string') {
      return theme.themeInfo?.loginImage
    } else {
      return URL.createObjectURL(theme.themeInfo?.loginImage)
    }
  } else {
    return ''
  }
})

const loginImage = computed(() => {
  if (theme.themeInfo?.loginImage) {
    return `${fileURL.value}`
  } else {
    const imgName = getThemeImg(theme.themeInfo?.theme)
    const imgPath = `${window.MaxKB.prefix}/theme/${imgName}.jpg`
    const imageUrl = new URL(imgPath, import.meta.url).href
    return imageUrl
  }
})
</script>
<style lang="scss" scoped>
.login-warp {
  height: 100vh;

  .login-image {
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
    width: 100%;
    height: 100%;
  }
  .right-container {
    position: relative;
    .lang {
      position: absolute;
      right: 20px;
      top: 20px;
    }
  }
}
</style>
