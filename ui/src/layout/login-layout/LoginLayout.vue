<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <div class="login-background">
        <div class="floating-shape shape-1"></div>
        <div class="floating-shape shape-2"></div>
        <div class="floating-shape shape-3"></div>
        <div class="floating-shape shape-4"></div>
        <div class="warm-gradient-circle circle-1"></div>
        <div class="warm-gradient-circle circle-2"></div>
      </div>
      <div class="login-content flex-center">
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
          <el-button class="lang-button">
            {{ currentLanguage }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
        </el-dropdown>
        <slot></slot>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import useStore from '@/stores'
import { useLocalStorage } from '@vueuse/core'
import { langList, localeConfigKey, getBrowserLang } from '@/locales/index'
defineProps({
  lang: {
    type: Boolean,
    default: true,
  },
})
const { user } = useStore()

const changeLang = (lang: string) => {
  useLocalStorage(localeConfigKey, getBrowserLang()).value = lang
  window.location.reload()
}

const currentLanguage = computed(() => {
  return langList.value?.filter((v: any) => v.value === user.getLanguage())?.[0]?.label
})
</script>
<style lang="scss" scoped>
.login-warp {
  height: 100vh;
  overflow: hidden;
}

.login-container {
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #fff5e6 0%, #ffe4c9 25%, #ffd8b8 50%, #ffccb3 75%, #ffd8b8 100%);
  overflow: hidden;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  animation: float 20s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #ff9a56 0%, #ff6b35 100%);
  top: -100px;
  right: -50px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #ffcc80 0%, #ffa726 100%);
  bottom: -50px;
  left: -30px;
  animation-delay: -5s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, #ffb74d 0%, #ff9800 100%);
  top: 30%;
  left: 10%;
  animation-delay: -10s;
}

.shape-4 {
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, #ffe0b2 0%, #ffcc80 100%);
  bottom: 20%;
  right: 15%;
  animation-delay: -15s;
}

.warm-gradient-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #ff7043 0%, transparent 70%);
  top: -100px;
  left: -100px;
}

.circle-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #ffb300 0%, transparent 70%);
  bottom: -150px;
  right: -100px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  25% {
    transform: translateY(-30px) rotate(90deg);
  }
  50% {
    transform: translateY(0px) rotate(180deg);
  }
  75% {
    transform: translateY(30px) rotate(270deg);
  }
}

.login-content {
  position: relative;
  z-index: 1;
  height: 100%;
  padding: 20px;
}

.lang {
  position: absolute;
  right: 20px;
  top: 20px;
  z-index: 10;
}

.lang-button {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 152, 0, 0.3);
  color: #e65100;
  backdrop-filter: blur(10px);
  border-radius: 25px;
  padding: 8px 20px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.95);
    border-color: #ff9800;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
  }
}
</style>
