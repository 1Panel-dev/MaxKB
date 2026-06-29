<template>
  <div class="login-warp">
    <div class="login-container w-full h-full">
      <el-row class="container w-full h-full">
        <el-col :xs="0" :sm="0" :md="10" :lg="10" :xl="10" class="left-container">
          <div class="login-left-bg">
            <!-- 装饰性光斑 -->
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <!-- Logo 区域 -->
            <div class="login-brand">
              <img src="@/assets/logo/logo.png" alt="logo" class="login-logo" />
              <h1 class="login-title">MaxKB</h1>
              <p class="login-slogan">{{ newDefaultSlogan }}</p>
            </div>
          </div>
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
import useStore from '@/stores'
import { useLocalStorage } from '@vueuse/core'
import { langList, localeConfigKey, getBrowserLang } from '@/locales/index'
import { t } from '@/locales'

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

const newDefaultSlogan = computed(() => {
  const default_login = '强大易用的企业级智能体平台'
  if (!theme.themeInfo?.slogan || default_login == theme.themeInfo?.slogan) {
    return t('theme.defaultSlogan')
  } else {
    return theme.themeInfo?.slogan
  }
})
</script>
<style lang="scss" scoped>
.login-warp {
  height: 100vh;
  background: var(--bg-content);
}

.left-container {
  position: relative;
  overflow: hidden;
}

.login-left-bg {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E8F0FE 0%, #C5D9FC 50%, #E5E0FA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

// 装饰性光斑
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
}
.orb-1 {
  width: 300px;
  height: 300px;
  background: rgba(26, 109, 255, 0.2);
  top: 10%;
  left: 10%;
}
.orb-2 {
  width: 250px;
  height: 250px;
  background: rgba(127, 59, 245, 0.15);
  bottom: 20%;
  right: 10%;
}
.orb-3 {
  width: 200px;
  height: 200px;
  background: rgba(197, 217, 252, 0.3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.login-brand {
  position: relative;
  z-index: 1;
  text-align: center;
}

.login-logo {
  width: 120px;
  height: auto;
  margin-bottom: 24px;
}

.login-title {
  font-size: 32px;
  font-weight: 700;
  color: #1A6DFF;
  margin-bottom: 12px;
}

.login-slogan {
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 300px;
}

.right-container {
  position: relative;
  .lang {
    position: absolute;
    right: 20px;
    top: 20px;
  }
}

// 暗色模式左侧渐变
[data-theme="dark"] .login-left-bg {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
}

[data-theme="dark"] .login-title {
  color: #5A94F5;
}

[data-theme="dark"] .orb-1 {
  background: rgba(61, 133, 255, 0.15);
}
[data-theme="dark"] .orb-2 {
  background: rgba(127, 59, 245, 0.1);
}
[data-theme="dark"] .orb-3 {
  background: rgba(90, 148, 245, 0.1);
}
</style>
