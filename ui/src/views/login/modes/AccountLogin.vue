<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import ExternalLoginApi from '@/api/admin/auth/external-login'
import LoginApi from '@/api/admin/auth/login'
import { LOGIN_METHOD_LABELS } from '@/constants/auth'
import { useStore } from '@/stores'
import type { LoginConfig, LoginMethod } from '@/api/types'
import { MsgConfirm, MsgError } from '@/utils/message'

interface AccountLoginForm {
  captcha: string
  password: string
  username: string
}

defineOptions({ name: 'AccountLogin' })

const props = defineProps<{
  loginConfig?: LoginConfig
}>()

const route = useRoute()
const router = useRouter()
const { auth } = useStore()
const isSubmitting = ref(false)
const identifyCode = ref('')
const loginMethod = ref<LoginMethod>(props.loginConfig?.default_value ?? 'LOCAL')

const accountLoginMethods = computed(() => {
  let loginMethods = [...(props.loginConfig?.login_methods ?? [])]
  if (loginMethods.includes('LOCAL')) {
    loginMethods = ['LOCAL', ...loginMethods.filter((method) => method !== 'LOCAL')]
  } else if (loginMethods.includes('LDAP')) {
    loginMethods = ['LDAP', ...loginMethods.filter((method) => method !== 'LDAP')]
  }
  if (loginMethods.length === 1 && loginMethods[0] === 'LOCAL') return []

  return loginMethods
})

const accountLoginFormRef = ref<FormInstance>()
const accountLoginForm = reactive<AccountLoginForm>({
  captcha: '',
  password: '',
  username: '',
})

const accountLoginRules = reactive<FormRules<AccountLoginForm>>({
  captcha: [{ required: false, message: '请输入验证码', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
})

const handleLogin = async () => {
  if (!accountLoginFormRef.value) return

  await accountLoginFormRef.value.validate((valid) => {
    if (valid) {
      isSubmitting.value = true
      if (loginMethod.value === 'LDAP') {
        auth
          .asyncLdapLogin(accountLoginForm)
          .then(() => {
            router.push({ name: 'workspace-home', params: { workspaceId: 'default' } })
          })
          .catch(() => {
            isSubmitting.value = false
          })
      } else {
        const encryptor = new JSEncrypt()
        encryptor.setPublicKey(auth.baseProfile?.rsa ?? '')
        const encryptedData = encryptor.encrypt(JSON.stringify(accountLoginForm))
        if (!encryptedData) {
          MsgError('登录信息加密失败')
          isSubmitting.value = false
          return
        }

        auth
          .asyncLogin({
            encryptedData,
            password: '',
            username: accountLoginForm.username,
          })
          .then(() => {
            router.push({ name: 'workspace-home', params: { workspaceId: 'default' } })
          })
          .catch(() => {
            isSubmitting.value = false
            refreshCaptcha()
          })
      }
    }
  })
}

const refreshCaptcha = () => {
  if (loginMethod.value === 'LDAP') return
  identifyCode.value = ''
  LoginApi.getCaptcha(accountLoginForm.username).then((res) => {
    identifyCode.value = res.captcha
  })
}

const selectLoginMethod = (method: LoginMethod) => {
  if (method !== 'LOCAL' && method !== 'LDAP') {
    void redirectExternalLogin(method, true)
    return
  }
  loginMethod.value = method
  Object.assign(accountLoginForm, { captcha: '', password: '', username: '' })
  identifyCode.value = ''
  accountLoginFormRef.value?.clearValidate()
}

const redirectExternalLogin = async (method: LoginMethod, needConfirm: boolean) => {
  const redirectUrl = await getExternalLoginUrl(method)
  if (!redirectUrl) return
  if (needConfirm) {
    return MsgConfirm('跳转提示', '即将跳转至外部认证页面，是否继续？', {
      confirmButtonText: '跳转',
    })
      .then(() => {
        window.location.href = redirectUrl
      })
      .catch(() => {})
  }
  window.location.href = redirectUrl
}

const getExternalLoginUrl = (authType: LoginMethod): Promise<string> => {
  if (authType === 'SAML2') return ExternalLoginApi.getSamlLoginUrl()

  return ExternalLoginApi.getExternalAuthSetting(authType).then(({ config }) => {
    if (!config) return ''

    const redirectUrl = `${config.redirectUrl}`
    if (authType === 'CAS') {
      if (!config.ldpUri) return ''
      const separator = config.ldpUri.includes('?') ? '&' : '?'
      return `${config.ldpUri}${separator}service=${encodeURIComponent(redirectUrl)}`
    }
    if (authType === 'OIDC') {
      if (!config.authEndpoint || !config.clientId) return ''
      const scope = config.scope || 'openid+profile+email'
      let url = `${config.authEndpoint}?client_id=${config.clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}`
      if (config.state) url += `&state=${config.state}`
      return url
    }
    if (authType === 'OAuth2') {
      if (!config.authEndpoint || !config.clientId) return ''
      let url = `${config.authEndpoint}?client_id=${config.clientId}&response_type=code&redirect_uri=${redirectUrl}&state=${crypto.randomUUID()}`
      if (config.scope) url += `&scope=${config.scope}`
      return url
    }

    return ''
  })
}

onMounted(() => {
  const loginMethods = accountLoginMethods.value
  if (route.query.login_mode !== 'manual') {
    const loginMethod = loginMethods[0]
    if (
      loginMethod &&
      ['CAS', 'OIDC', 'OAuth2', 'SAML2'].some((authType) => authType === loginMethod)
    ) {
      void redirectExternalLogin(loginMethod, false)
    }
  }
})
</script>

<template>
  <div class="flex h-full flex-col">
    <div class="min-h-0 flex-1">
      <h2 class="mb-4">
        {{ loginMethod === 'LDAP' ? 'LDAP 登录' : LOGIN_METHOD_LABELS[loginMethod] }}
      </h2>

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
        <div v-if="loginMethod !== 'LDAP' && identifyCode" class="flex gap-2">
          <el-form-item prop="captcha" class="flex-1">
            <el-input
              v-model="accountLoginForm.captcha"
              autocomplete="off"
              placeholder="请输入验证码"
            />
          </el-form-item>
          <img
            :src="identifyCode"
            alt="验证码"
            class="w-35 h-10 cursor-pointer border"
            @click="refreshCaptcha"
          />
        </div>
        <el-form-item>
          <el-button :loading="isSubmitting" native-type="submit" type="primary" class="w-full"
            >登录</el-button
          >
        </el-form-item>
      </el-form>
      <el-button
        size="default"
        class="mt-3"
        link
        type="primary"
        @click="router.push({ name: 'forgot-password' })"
      >
        忘记密码？
      </el-button>
    </div>
    <div v-if="accountLoginMethods.length" class="third-login flex-col-center gap-4">
      <el-divider>其他登录方式</el-divider>
      <div class="flex gap-4">
        <template v-for="method in accountLoginMethods" :key="method">
          <el-button
            circle
            size="large"
            class="text-xs! font-medium!"
            @click="selectLoginMethod(method)"
            v-if="loginMethod !== method"
          >
            <MkIcon v-if="method === 'LOCAL'" name="icon_pc_outlined" :size="22.5" />
            <span v-else>{{ method }}</span>
          </el-button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
