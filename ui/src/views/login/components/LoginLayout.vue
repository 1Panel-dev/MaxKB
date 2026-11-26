<script setup lang="ts">
import { computed } from 'vue'
import { CaretBottom } from '@element-plus/icons-vue'
import type { ThemeInfo } from '@/api/admin/auth/types'
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import DefaultThemeAnimation from './DefaultThemeAnimation.vue'
import { DEFAULT_THEME_COLOR, DEFAULT_THEME_SETTING, getThemeImg } from '@/constants'
import { LOCALE_OPTIONS, resolveSupportedLocale } from '@/locales/config'
import { useStore } from '@/stores'

defineOptions({ name: 'LoginLayout' })

const props = withDefaults(defineProps<{ preview?: boolean; themeInfo?: ThemeInfo }>(), { preview: false })

defineSlots<{ default: () => unknown }>()

const { theme, user } = useStore()
const currentLocale = computed(() => resolveSupportedLocale(user.language))
const currentLanguageLabel = computed(() => LOCALE_OPTIONS.find((option) => option.value === currentLocale.value)?.label)

const layoutThemeInfo = computed(() => props.themeInfo ?? theme.themeInfo)
const customLoginImage = computed(() => layoutThemeInfo.value?.loginImage?.trim() ?? '')
const isDefaultTheme = computed(() => !layoutThemeInfo.value?.theme || layoutThemeInfo.value.theme === DEFAULT_THEME_COLOR)
const showDefaultThemeAnimation = computed(() => !props.preview && !customLoginImage.value && isDefaultTheme.value)
const loginImage = computed(() => customLoginImage.value || getThemeImg(layoutThemeInfo.value?.theme))
</script>

<template>
  <div class="login-layout" :class="{ 'is-preview': preview }">
    <div class="login-background"></div>

    <header class="login-header flex-between mb-6">
      <div class="flex-align-center gap-4">
        <img v-if="layoutThemeInfo?.loginLogo" :src="layoutThemeInfo.loginLogo" alt="MaxKB" class="h-9.5 max-w-50 object-contain object-left" />
        <LogoFull v-else height="38" />
        <el-divider v-if="layoutThemeInfo?.slogan" direction="vertical" />
        <span class="text-lg">{{ layoutThemeInfo?.slogan ?? DEFAULT_THEME_SETTING.slogan }}</span>
      </div>
      <!-- 切换登录界面语言 -->
      <MkDropdown v-if="!preview" trigger="click" placement="bottom-end">
        <el-button text class="flex-align-center gap-1">
          <MkIcon name="icon_internet_outlined" class="shrink-0" :size="16" />
          <span>{{ currentLanguageLabel }}</span>
          <MkIcon :icon="CaretBottom" :size="14" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu class="w-52">
            <template v-for="option in LOCALE_OPTIONS" :key="option.value">
              <MkDropdownItem selectable :selected="currentLocale === option.value" @click="user.setLanguage(option.value)">
                {{ option.label }}
              </MkDropdownItem>
            </template>
          </MkDropdownMenu>
        </template>
      </MkDropdown>
    </header>
    <el-scrollbar height="100%" view-class="h-full">
      <el-row class="login-main p-6 pt-19" align="middle">
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
    </el-scrollbar>
  </div>
</template>

<style scoped lang="scss">
.login-layout {
  background: var(--mk-N100);
  height: 100vh;
  overflow: hidden;
  position: relative;

  &.is-preview {
    height: 100%;
    min-height: 0;
  }
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
  min-height: 100%;
  margin: 0 auto;
  max-width: 1120px;
  position: relative;
}
.login-card {
  --el-card-padding: 40px;
  height: 526px;
  position: relative;
  border: none;
}
</style>
