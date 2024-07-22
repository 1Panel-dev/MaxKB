<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <el-row class="container w-full h-full">
        <el-col :xs="0" :sm="0" :md="10" :lg="10" :xl="10" class="left-container">
          <div class="login-image" :style="{ backgroundImage: `url(${loginImage})` }"></div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="14" :lg="14" :xl="14" class="right-container flex-center">
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
import { request } from '@/request'
defineOptions({ name: 'LoginLayout' })
const { user } = useStore()

const fileURL = computed(() => {
  if (user.themeInfo?.loginImage) {
    if (typeof user.themeInfo?.loginImage === 'string') {
      return user.themeInfo?.loginImage
    } else {
      return URL.createObjectURL(user.themeInfo?.loginImage)
    }
  } else {
    return ''
  }
})

const loginImage = computed(() => {
  if (user.themeInfo?.loginImage) {
    return `${fileURL.value}`
  } else {
    return new URL(`../../assets/theme/${getThemeImg(user.themeInfo?.theme)}.jpg`, import.meta.url)
      .href
  }
})
</script>
<style lang="scss" scope>
.login-warp {
  height: 100vh;

  .login-image {
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
    width: 100%;
    height: 100%;
  }
}
</style>
