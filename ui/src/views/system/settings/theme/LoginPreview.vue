<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { Close } from '@element-plus/icons-vue'
import type { ThemeInfo } from '@/api/admin/auth/types'
import defaultLogo from '@/assets/mk-logo/MaxKB-logo.svg'
import LogoFull from '@/components/mk-logo/LogoFull.vue'

type ThemeImageValue = File | string
type ThemePreviewData = Omit<ThemeInfo, 'icon' | 'loginImage' | 'loginLogo'> & {
  icon?: ThemeImageValue
  loginImage?: ThemeImageValue
  loginLogo?: ThemeImageValue
}

defineOptions({ name: 'ThemeLoginPreview' })

const props = defineProps<{
  data: ThemePreviewData
}>()

function useImageSource(source: () => ThemeImageValue | undefined, fallback: string) {
  const imageSource = ref(fallback)
  let objectUrl: string | undefined

  watch(
    source,
    (value) => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
      objectUrl = value instanceof File ? URL.createObjectURL(value) : undefined
      imageSource.value = objectUrl ?? (typeof value === 'string' && value ? value : fallback)
    },
    { immediate: true },
  )

  onBeforeUnmount(() => {
    if (objectUrl) URL.revokeObjectURL(objectUrl)
  })

  return imageSource
}

const websiteIcon = useImageSource(() => props.data.icon, defaultLogo)
const loginLogo = useImageSource(() => props.data.loginLogo, '')
</script>

<template>
  <div class="login-preview overflow-hidden rounded-md border">
    <div class="browser-bar flex items-end px-2">
      <div class="browser-tab flex items-center gap-2 rounded-t-md bg-white px-3">
        <img :src="websiteIcon" alt="" class="h-4 w-4 object-contain" />
        <span class="min-w-0 flex-1 truncate" :title="data.title || 'MaxKB'">
          {{ data.title || 'MaxKB' }}
        </span>
        <el-icon :size="12"><Close /></el-icon>
      </div>
    </div>

    <div class="preview-page relative overflow-hidden">
      <header class="preview-header flex items-center gap-3">
        <img
          v-if="loginLogo"
          :src="loginLogo"
          alt="MaxKB"
          class="h-8 max-w-40 object-contain object-left"
        />
        <LogoFull v-else class="h-8 max-w-40" />
        <el-divider v-if="data.slogan" direction="vertical" />
        <span class="truncate text-N600" :title="data.slogan || ''">{{ data.slogan }}</span>
      </header>

      <div class="preview-content grid h-full grid-cols-2 items-center gap-8 px-10 pt-10">
        <!-- <img :src="defaultDecoration" alt="" class="w-full object-contain" /> -->
        <el-card class="preview-login-card">
          <h3 class="mb-6">登录</h3>
          <el-input class="mb-4" placeholder="请输入用户名" size="large" />
          <el-input class="mb-4" placeholder="请输入密码" size="large" type="password" />
          <el-button class="w-full" size="large" type="primary">登录</el-button>
          <el-button class="mt-2 !ml-0" link type="primary">忘记密码？</el-button>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.browser-bar {
  background: var(--mk-N200);
  height: 36px;
}

.browser-tab {
  height: 30px;
  max-width: 220px;
  width: 40%;
}

.preview-content {
  position: relative;
  z-index: 1;
}

.preview-header {
  left: 24px;
  position: absolute;
  right: 24px;
  top: 16px;
  z-index: 2;
}

.preview-login-card {
  --el-card-padding: 24px;
  justify-self: end;
  max-width: 320px;
  width: 100%;
}

.preview-page {
  background-position: center;
  background-size: cover;
  height: 420px;
}
</style>
