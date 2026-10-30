<script setup lang="ts">
import { onBeforeMount, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getDingTalkClientAuthCode } from './dingtalk-client-login'
import BaseInfoApi from '@/api/admin/auth/base-info.ts'
import { useStore } from '@/stores'
import { LOGIN_METHOD } from '@/api/enums'
import type { LoginConfig } from '@/api/types'
import LoginLayout from './components/LoginLayout.vue'
import LoginModePanel from './components/LoginModePanel.vue'
import { useAdminLoginService } from './admin-login-service'

const route = useRoute()
const { auth } = useStore()
const loginService = useAdminLoginService()

const isLoading = ref(true)
const loginConfig = ref<LoginConfig>({ default_value: LOGIN_METHOD.LOCAL, login_methods: [LOGIN_METHOD.LOCAL], max_attempts: 1 })

// 平台配置加载及客户端授权期间暂停普通登录，失败后恢复原登录方式。
onBeforeMount(async () => {
  isLoading.value = true
  try {
    await auth.loadPlatformProfile()
    if (auth.isPE || auth.isEE) {
      const config = await BaseInfoApi.getLoginConfig()
      if (Object.keys(config).length > 0) loginConfig.value = config
    }

    const code = await getDingTalkClientAuthCode(route.query)
    if (!code) return
    await auth.loginWithDingTalkClient(code)
    await loginService.onLoginSuccess()
  } catch {
    // 接口错误由请求层提示，保留普通登录入口。
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <LoginLayout v-if="!isLoading">
    <LoginModePanel :login-config="loginConfig" :login-service="loginService" />
  </LoginLayout>
</template>
