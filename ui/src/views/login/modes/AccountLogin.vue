<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import JSEncrypt from 'jsencrypt'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import externalLoginApi from '@/api/admin/auth/external-login'
import loginApi from '@/api/admin/auth/login'
import type { LoginConfig } from '@/api/admin/auth/types'
import { useStore } from '@/stores'
import { MsgConfirm, MsgError } from '@/utils/message'
import { loginMethodLabels, qrCodeLoginMethods } from '../constants'
import type { AccountLoginForm, LoginMethod } from '../types'

defineOptions({ name: 'AccountLogin' })

const props = defineProps<{
  loginConfig?: LoginConfig
  rsaPublicKey?: string
}>()

const router = useRouter()
const { login } = useStore()
const isSubmitting = ref(false)
const captchaImage = ref('')
const loginMethod = ref<LoginMethod>('LOCAL')
const accountLoginMethods = computed(() =>
  (props.loginConfig?.login_methods ?? [])
    .filter(
      (method) => method !== 'LOCAL' && !qrCodeLoginMethods.some((provider) => provider === method),
    )
    .map((method) => ({ label: loginMethodLabels[method], value: method })),
)

const accountLoginFormRef = ref<FormInstance>()
const accountLoginForm = reactive<AccountLoginForm>({
  captcha: '',
  password: '',
  username: '',
})

const accountLoginRules: FormRules<AccountLoginForm> = {
  captcha: [{ required: false, message: '请输入验证码', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!accountLoginFormRef.value) return
  const valid = await accountLoginFormRef.value.validate().catch(() => false)
  if (!valid) return

  let loginRequest: Promise<void>
  if (loginMethod.value === 'LDAP') {
    loginRequest = login.asyncLdapLogin(accountLoginForm)
  } else {
    const encryptor = new JSEncrypt()
    encryptor.setPublicKey(props.rsaPublicKey ?? '')
    const encryptedData = encryptor.encrypt(JSON.stringify(accountLoginForm))
    if (!encryptedData) {
      MsgError('登录信息加密失败')
      return
    }
    loginRequest = login.asyncLogin({
      encryptedData,
      username: accountLoginForm.username,
      password: '',
    })
  }

  isSubmitting.value = true
  loginRequest
    .then(
      () => router.push({ name: 'workspace-home', params: { workspaceId: 'default' } }),
      () => refreshCaptcha(),
    )
    .finally(() => {
      isSubmitting.value = false
    })
}

const refreshCaptcha = () => {
  if (loginMethod.value === 'LDAP') return
  captchaImage.value = ''
  return loginApi.getCaptcha(accountLoginForm.username).then((captcha) => {
    captchaImage.value = captcha.captcha
  })
}

const selectLoginMethod = async (method: LoginMethod) => {
  if (method !== 'LOCAL' && method !== 'LDAP') {
    const redirectUrl = await getExternalLoginUrl(method)
    if (!redirectUrl) return
    await MsgConfirm('跳转提示', '即将跳转至外部认证页面，是否继续？', {
      confirmButtonText: '跳转',
    })
    window.location.href = redirectUrl
    return
  }
  loginMethod.value = method
  Object.assign(accountLoginForm, { captcha: '', password: '', username: '' })
  captchaImage.value = ''
  accountLoginFormRef.value?.clearValidate()
}

const getExternalLoginUrl = (authType: LoginMethod): Promise<string> => {
  if (authType === 'SAML2') return externalLoginApi.getSamlLoginUrl()
  return externalLoginApi.getExternalAuthSetting(authType).then(({ config }) => {
    if (!config) return ''
    if (authType === 'CAS' && config.ldpUri) {
      const separator = config.ldpUri.includes('?') ? '&' : '?'
      return `${config.ldpUri}${separator}service=${encodeURIComponent(config.redirectUrl)}`
    }
    if (!['OIDC', 'OAuth2'].includes(authType) || !config.authEndpoint || !config.clientId)
      return ''
    const params = new URLSearchParams({
      client_id: config.clientId,
      redirect_uri: config.redirectUrl,
      response_type: 'code',
    })
    if (authType === 'OAuth2') params.set('state', crypto.randomUUID())
    if (config.state && authType === 'OIDC') params.set('state', config.state)
    if (config.scope || authType === 'OIDC') {
      params.set('scope', config.scope || 'openid profile email')
    }
    return `${config.authEndpoint}?${params}`
  })
}

watch(
  () => props.loginConfig?.default_value,
  (method) => {
    if (method === 'LOCAL' || method === 'LDAP') loginMethod.value = method
  },
  { immediate: true },
)

watch(
  () => props.loginConfig,
  (config) => {
    if (!config) return
    const methods = config.login_methods ?? []
    const hasEmbeddedLogin = methods.some(
      (method) =>
        method === 'LOCAL' ||
        method === 'LDAP' ||
        qrCodeLoginMethods.some((provider) => provider === method),
    )
    if (!hasEmbeddedLogin) {
      void getExternalLoginUrl(config.default_value).then((url) => {
        if (url) window.location.href = url
      })
    }
  },
)
</script>

<template>
  <div class="flex h-full flex-col">
    <div class="min-h-0 flex-1">
      <h2 class="mb-4">账号登录</h2>

      <el-form
        ref="accountLoginFormRef"
        :model="accountLoginForm"
        :rules="accountLoginRules"
        class="login-form"
        @submit.prevent="handleLogin"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="accountLoginForm.username"
            placeholder="请输入用户名"
            @blur="refreshCaptcha"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="accountLoginForm.password"
            placeholder="请输入密码"
            show-password
            type="password"
          />
        </el-form-item>
        <div v-if="loginMethod !== 'LDAP' && captchaImage" class="flex gap-2">
          <el-form-item prop="captcha" class="flex-1">
            <el-input
              v-model="accountLoginForm.captcha"
              autocomplete="off"
              placeholder="请输入验证码"
            />
          </el-form-item>
          <button
            type="button"
            class="h-10 overflow-hidden rounded-md"
            aria-label="刷新验证码"
            @click="refreshCaptcha"
          >
            <img :src="captchaImage" alt="验证码" class="h-full" />
          </button>
        </div>
        <el-form-item>
          <el-button :loading="isSubmitting" native-type="submit" type="primary" class="w-full"
            >登录</el-button
          >
        </el-form-item>
      </el-form>
      <el-button
        size="default"
        class="-mt-2"
        link
        type="primary"
        @click="router.push({ name: 'forgot-password' })"
      >
        忘记密码？
      </el-button>
    </div>
    <div v-if="accountLoginMethods.length" class="third-login flex-col-center gap-4">
      <el-divider>其他登录方式</el-divider>
      <div>
        <el-button
          v-for="method in accountLoginMethods"
          :key="method.value"
          circle
          size="large"
          class="text-xs! font-medium!"
          @click="selectLoginMethod(method.value)"
        >
          {{ method.label }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
