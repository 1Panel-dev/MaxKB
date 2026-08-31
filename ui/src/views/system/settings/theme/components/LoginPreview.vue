<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { Close } from '@element-plus/icons-vue'
import type { ThemeInfo } from '@/api/admin/auth/types'
import { LOGIN_METHOD } from '@/api/enums'
import type { LoginConfig } from '@/api/types'
import LogoIcon from '@/components/mk-logo/LogoIcon.vue'
import { getThemeImg } from '@/constants/theme'
import LoginLayout from '@/views/login/components/LoginLayout.vue'
import AccountLogin from '@/views/login/modes/AccountLogin.vue'

type ThemeImageValue = File | string
type ThemePreviewData = Omit<ThemeInfo, 'icon' | 'loginImage' | 'loginLogo'> & {
  icon?: ThemeImageValue
  loginImage?: ThemeImageValue
  loginLogo?: ThemeImageValue
}

defineOptions({ name: 'ThemeLoginPreview' })

const props = defineProps<{ data: ThemePreviewData }>()
const previewLoginConfig: LoginConfig = {
  default_value: LOGIN_METHOD.LOCAL,
  login_methods: [LOGIN_METHOD.LOCAL, LOGIN_METHOD.LDAP, LOGIN_METHOD.CAS, LOGIN_METHOD.OAUTH2, LOGIN_METHOD.OIDC],
  max_attempts: 1,
}

function useImageSource(source: () => ThemeImageValue | undefined, fallback: () => string) {
  const imageSource = ref(fallback())
  let objectUrl: string | undefined

  watch(
    () => [source(), fallback()] as const,
    ([value, fallbackValue]) => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
      objectUrl = value instanceof File ? URL.createObjectURL(value) : undefined
      imageSource.value = objectUrl ?? (typeof value === 'string' && value ? value : fallbackValue)
    },
    { immediate: true },
  )

  onBeforeUnmount(() => {
    if (objectUrl) URL.revokeObjectURL(objectUrl)
  })

  return imageSource
}

const defaultLoginImage = computed(() => getThemeImg(props.data.theme))

const websiteIcon = useImageSource(
  () => props.data.icon,
  () => '',
)
const loginLogo = useImageSource(
  () => props.data.loginLogo,
  () => '',
)
const loginImage = useImageSource(
  () => props.data.loginImage,
  () => defaultLoginImage.value,
)
const previewThemeInfo = computed<ThemeInfo>(() => ({
  ...props.data,
  icon: websiteIcon.value,
  loginImage: loginImage.value,
  loginLogo: loginLogo.value,
}))
</script>

<template>
  <div class="login-preview overflow-hidden rounded-md">
    <div class="browser-bar flex items-end px-2">
      <div class="browser-tab flex items-center gap-2 rounded-t-md bg-white px-2">
        <img v-if="websiteIcon" :src="websiteIcon" alt="" class="size-4 object-contain" />
        <LogoIcon v-else class="h-4" />
        <span class="min-w-0 flex-1 truncate font-semibold text-sm" :title="data.title || 'MaxKB'">
          {{ data.title || 'MaxKB' }}
        </span>
        <MkIcon name="icon_close_outlined" :size="12" />
      </div>
    </div>

    <div class="preview-page relative overflow-hidden">
      <div class="preview-scale" inert>
        <LoginLayout preview :theme-info="previewThemeInfo">
          <AccountLogin preview :login-config="previewLoginConfig" />
        </LoginLayout>
      </div>
      <div class="preview-mask absolute inset-0" aria-hidden="true"></div>
    </div>
  </div>
</template>

<style scoped lang="scss">
/* browser */
.browser-bar {
  background: var(--mk-N200);
  height: 36px;
}

.browser-tab {
  height: 30px;
  max-width: 220px;
}

/* preview */
.preview-mask {
  position: absolute;
  z-index: 20;
}

.preview-page {
  height: 420px;
}

.preview-scale {
  height: 840px;
  transform: scale(0.5);
  transform-origin: left top;
  width: 200%;
}
</style>
