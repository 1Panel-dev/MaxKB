<script setup lang="ts">
import { computed } from 'vue'
import type { CSSProperties } from 'vue'
import defaultBackgroundImage from '@/assets/mk-login-background.png'

defineOptions({ name: 'LoginLayout' })

const props = withDefaults(
  defineProps<{
    backgroundImage?: string
    preview?: boolean
    themeColor?: string
    websiteName?: string
    welcomeText?: string
  }>(),
  {
    backgroundImage: defaultBackgroundImage,
    preview: false,
    themeColor: '#3370ff',
    websiteName: 'MaxKB',
    welcomeText: '强大易用的企业级智能体平台',
  },
)

defineSlots<{
  default: () => unknown
}>()

const backgroundStyle = computed<CSSProperties>(() => ({
  backgroundImage: `url("${props.backgroundImage}")`,
}))
</script>

<template>
  <div class="login-layout">
    <div class="login-background" :style="backgroundStyle"></div>

    <header class="login-header flex-between">
      <div class="flex items-center gap-4">
        <img src="@/assets/logo/MaxKB-logo.svg" />
        <el-divider direction="vertical" v-if="welcomeText" />
        <span class="text-lg">{{ welcomeText }}</span>
      </div>
    </header>

    <el-row class="login-main" align="middle">
      <el-col :xs="0" :sm="0" :md="13" :lg="13" class="login-decoration">
        <img src="@/assets/login-theme/default.png" alt="" />
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
