<script setup lang="ts">
import { onBeforeMount, ref } from 'vue'
import BaseInfoApi from '@/api/admin/auth/base-info.ts'
import { useStore } from '@/stores'
import { LOGIN_METHOD } from '@/api/enums'
import type { LoginConfig } from '@/api/types'
import LoginLayout from './components/LoginLayout.vue'
import LoginModePanel from './components/LoginModePanel.vue'
import { useAdminLoginService } from './admin-login-service'

const { auth } = useStore()
const loginService = useAdminLoginService()

const isLoading = ref(true)
const loginConfig = ref<LoginConfig>({ default_value: LOGIN_METHOD.LOCAL, login_methods: [LOGIN_METHOD.LOCAL], max_attempts: 1 })

onBeforeMount(() => {
  // 登录配置加载完成后，按默认登录方式挂载对应模式。
  isLoading.value = true
  auth
    .loadPlatformProfile()
    .then(() => {
      if (auth.isPE || auth.isEE) {
        return BaseInfoApi.getLoginConfig().then((config) => {
          if (Object.keys(config).length > 0) {
            loginConfig.value = config
          } else {
            loginConfig.value = { max_attempts: 1, default_value: LOGIN_METHOD.LOCAL, login_methods: [LOGIN_METHOD.LOCAL] }
          }
        })
      }
      loginConfig.value = { max_attempts: 1, default_value: LOGIN_METHOD.LOCAL, login_methods: [LOGIN_METHOD.LOCAL] }
    })
    .finally(() => {
      isLoading.value = false
    })
})
</script>

<template>
  <LoginLayout v-if="!isLoading">
    <LoginModePanel :login-config="loginConfig" :login-service="loginService" />
  </LoginLayout>
</template>
