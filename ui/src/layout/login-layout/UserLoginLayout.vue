<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <div class="flex-center w-full h-full">
        <slot></slot>
      </div>
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
    const imgPath = `/theme/${imgName}.jpg`
    const imageUrl = new URL(imgPath, import.meta.url).href
    return imageUrl
  }
})
</script>
<style lang="scss" scoped>
.login-warp {
  height: 100vh;
}
</style>
