<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import ChatAuthApi from '@/api/chat/auth'
import type { ApplicationAuthProfileMeta } from '@/api/types'
import { useStore } from '@/stores/chat'

interface ChatLoginForm {
  captcha: string
  password: string
  username: string
}

defineOptions({ name: 'ChatLogin' })

// 门户登录与单应用登录共用本页，场景由守卫切换到 Store 的当前认证场景
const route = useRoute()
const router = useRouter()
const { auth } = useStore()

const loginTitle = computed(() => {
  if (auth.isPortal) return '门户登录'
  return (auth.authProfile?.meta as ApplicationAuthProfileMeta | undefined)?.application_name || '登录'
})

const isSubmitting = ref(false)
const identifyCode = ref('')
const loginFormRef = ref<FormInstance>()
const loginForm = reactive<ChatLoginForm>({ captcha: '', password: '', username: '' })

const loginRules = reactive<FormRules<ChatLoginForm>>({
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  username: [{ whitespace: true, required: true, message: '请输入用户名', trigger: 'blur' }],
})

// 验证码：后端按失败次数决定是否需要，无需时返回空字符串；目前仅应用场景支持
const refreshCaptcha = () => {
  const { accessToken } = auth
  if (!accessToken || !loginForm.username.trim()) return

  ChatAuthApi.getCaptcha(loginForm.username, accessToken).then(({ captcha }) => {
    identifyCode.value = captcha
  })
}

// 登录成功后回到守卫记录的原地址，没有时进入当前场景首页
const getRedirectRoute = (): RouteLocationRaw => {
  const { redirect } = route.query
  if (typeof redirect === 'string' && redirect.startsWith('/')) return redirect
  if (auth.accessToken) return { name: 'chat-home', params: { accessToken: auth.accessToken } }
  return { name: 'portal-home' }
}

const handleLogin = () => {
  loginFormRef.value?.validate((valid) => {
    if (!valid) return

    const encryptor = new JSEncrypt()
    encryptor.setPublicKey(auth.authProfile?.rsa_key ?? '')
    const encryptedData = encryptor.encrypt(JSON.stringify(loginForm))
    if (!encryptedData) return

    isSubmitting.value = true
    auth
      .login({ encryptedData, username: loginForm.username })
      .then(() => router.replace(getRedirectRoute()))
      .catch(() => {
        // 登录失败后失败次数可能达到上限，重新获取验证码
        loginForm.captcha = ''
        refreshCaptcha()
      })
      .finally(() => {
        isSubmitting.value = false
      })
  })
}
</script>

<template>
  <div class="chat-login flex-center">
    <el-card class="chat-login__card w-100">
      <img src="@/assets/mk-logo/MaxKB-logo.svg" alt="MaxKB" class="mb-8 h-9" />
      <h2 class="mb-6 truncate" :title="loginTitle">{{ loginTitle }}</h2>

      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" size="large" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" autocomplete="username" placeholder="请输入用户名" @blur="refreshCaptcha" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" autocomplete="current-password" placeholder="请输入密码" show-password type="password" />
        </el-form-item>
        <div v-if="identifyCode" class="flex gap-2">
          <el-form-item prop="captcha" class="flex-1">
            <el-input v-model="loginForm.captcha" autocomplete="off" placeholder="请输入验证码" />
          </el-form-item>
          <img :src="identifyCode" alt="验证码" class="w-35 h-10 cursor-pointer border" @click="refreshCaptcha" />
        </div>
        <el-form-item>
          <!-- 登录 -->
          <el-button :loading="isSubmitting" native-type="submit" type="primary" class="w-full">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.chat-login {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(var(--mk-primary-rgb) / 5%) 20%, rgba(var(--mk-primary-rgb) / 10%) 100%),
    var(--mk-N100);
  min-height: 100vh;
  padding: 16px;
}

.chat-login__card {
  --el-card-padding: 40px;
  border: none;
  max-width: 100%;
}
</style>
