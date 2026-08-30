<script setup lang="ts">
import { computed } from 'vue'
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import { DEFAULT_THEME_SETTING, getThemeImg } from '@/constants'
import { useStore } from '@/stores'
import DefaultThemeAnimation from './DefaultThemeAnimation.vue'

defineOptions({ name: 'LoginLayout' })

withDefaults(defineProps<{ preview?: boolean }>(), { preview: false })

defineSlots<{ default: () => unknown }>()

const { theme } = useStore()

const customLoginImage = computed(() => theme.themeInfo?.loginImage?.trim() ?? '')
const showDefaultThemeAnimation = computed(() => !customLoginImage.value && theme.isDefaultTheme)
const loginImage = computed(() => customLoginImage.value || getThemeImg(theme.themeInfo?.theme))
</script>

<template>
  <div class="login-layout">
    <div class="login-background"></div>

    <header class="login-header flex-between">
      <div class="flex items-center gap-4">
        <LogoFull height="38" />
        <el-divider direction="vertical" v-if="theme.themeInfo?.slogan" />
        <span class="text-lg">{{ theme.themeInfo?.slogan || DEFAULT_THEME_SETTING.slogan }}</span>
      </div>
    </header>

    <el-row class="login-main" align="middle">
      <el-col :xs="0" :sm="0" :md="13" :lg="13" class="login-decoration">
        <DefaultThemeAnimation v-if="showDefaultThemeAnimation" />
        <img v-else :src="loginImage" alt="" class="w-full object-contain" />
      </el-col>

      <el-col :xs="24" :sm="24" :md="11" :lg="11" class="flex-center!">
        <el-card class="login-card w-100">
          <slot />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.login-layout {
  background: var(--mk-N100);
  min-height: 100vh;
  overflow: hidden;
  position: relative;
}

.login-background {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(var(--mk-primary-rgb) / 5%) 20%, rgba(var(--mk-primary-rgb) / 10%) 100%);

  background-position: center;
  background-size: cover;
  inset: 0;
  position: absolute;
}

.login-header {
  left: 24px;
  position: absolute;
  right: 24px;
  top: 16px;
  z-index: 10;
}

.login-main {
  height: 100vh;
  margin: 0 auto;
  max-width: 1120px;
  position: relative;
}
.login-card {
  --el-card-padding: 40px;
  height: 526px;
  position: relative;
}
</style>
