<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { LOGIN_METHOD } from '@/api/enums'
import type { LoginConfig, LoginMethod } from '@/api/types'
import type { AccountLoginForm, LoginService } from '../types'

defineOptions({ name: 'AccountLogin' })

const props = withDefaults(defineProps<{ loginConfig?: LoginConfig; loginService: LoginService; preview?: boolean }>(), { preview: false })

const route = useRoute()
const isSubmitting = ref(false)
const identifyCode = ref('')
const loginMethod = ref<LoginMethod>(props.loginConfig?.default_value ?? LOGIN_METHOD.LOCAL)

const accountLoginMethods = computed(() => {
  let loginMethods = [...(props.loginConfig?.login_methods ?? [])]
  if (loginMethods.includes(LOGIN_METHOD.LOCAL)) {
    loginMethods = [LOGIN_METHOD.LOCAL, ...loginMethods.filter((method) => method !== LOGIN_METHOD.LOCAL)]
  } else if (loginMethods.includes(LOGIN_METHOD.LDAP)) {
    loginMethods = [LOGIN_METHOD.LDAP, ...loginMethods.filter((method) => method !== LOGIN_METHOD.LDAP)]
  }
  if (loginMethods.length === 1 && loginMethods[0] === LOGIN_METHOD.LOCAL) return []

  return loginMethods
})

const accountLoginFormRef = ref<FormInstance>()
const accountLoginForm = reactive<AccountLoginForm>({ captcha: '', password: '', username: '' })

const accountLoginRules = reactive<FormRules<AccountLoginForm>>({
  captcha: [{ required: false, message: '请输入验证码', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  username: [{ whitespace: true, required: true, message: '请输入用户名', trigger: 'blur' }],
})

const handleLogin = async () => {
  if (props.preview) return
  if (!accountLoginFormRef.value) return

  await accountLoginFormRef.value.validate((valid) => {
    if (valid) {
      isSubmitting.value = true
      if (loginMethod.value === LOGIN_METHOD.LDAP) {
        props.loginService
          .ldapLogin(accountLoginForm)
          .then(() => props.loginService.onLoginSuccess())
          .catch(() => {
            isSubmitting.value = false
          })
      } else {
        const encryptor = new JSEncrypt()
        encryptor.setPublicKey(props.loginService.rsaKey)
        const encryptedData = encryptor.encrypt(JSON.stringify(accountLoginForm))
        if (!encryptedData) {
          isSubmitting.value = false
          return
        }

        props.loginService
          .login({ encryptedData, username: accountLoginForm.username })
          .then(() => props.loginService.onLoginSuccess())
          .catch(() => {
            isSubmitting.value = false
            refreshCaptcha()
          })
      }
    }
  })
}

const refreshCaptcha = () => {
  if (props.preview) return
  if (loginMethod.value === LOGIN_METHOD.LDAP) return
  props.loginService.getCaptcha(accountLoginForm.username).then((captcha) => {
    identifyCode.value = captcha
  })
}

const selectLoginMethod = (method: LoginMethod) => {
  if (props.preview) return
  if (method !== LOGIN_METHOD.LOCAL && method !== LOGIN_METHOD.LDAP) {
    void redirectExternalLogin(method)
    return
  }
  loginMethod.value = method
  Object.assign(accountLoginForm, { captcha: '', password: '', username: '' })
  identifyCode.value = ''
  accountLoginFormRef.value?.clearValidate()
}

const redirectExternalLogin = async (method: LoginMethod) => {
  const redirectUrl = await props.loginService.getExternalLoginUrl(method)
  if (!redirectUrl) return
  window.location.href = redirectUrl
}

onMounted(() => {
  if (props.preview) return
  if (route.query.login_mode !== 'manual') {
    const defaultLoginMethod = loginMethod.value
    if ([LOGIN_METHOD.CAS, LOGIN_METHOD.OIDC, LOGIN_METHOD.OAUTH2, LOGIN_METHOD.SAML2].some((authType) => authType === defaultLoginMethod)) {
      void redirectExternalLogin(defaultLoginMethod)
    }
  }
})
</script>

<template>
  <div class="account-login flex-column h-full" :class="{ 'is-preview': preview }">
    <div class="min-h-0 flex-1">
      <h2 class="mb-4">
        {{ loginMethod === LOGIN_METHOD.LDAP ? 'LDAP 登录' : LOGIN_METHOD_LABELS[loginMethod] }}
      </h2>

      <el-form
        ref="accountLoginFormRef"
        :model="accountLoginForm"
        :rules="accountLoginRules"
        :autocomplete="preview ? 'off' : undefined"
        class="login-form"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="accountLoginForm.username"
            :autocomplete="preview ? 'off' : 'username'"
            :disabled="preview"
            :readonly="preview"
            placeholder="请输入用户名"
            @blur="refreshCaptcha"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="accountLoginForm.password"
            :autocomplete="preview ? 'new-password' : 'current-password'"
            :disabled="preview"
            :readonly="preview"
            placeholder="请输入密码"
            show-password
            type="password"
          />
        </el-form-item>
        <div v-if="loginMethod !== LOGIN_METHOD.LDAP && identifyCode" class="flex gap-2">
          <el-form-item prop="captcha" class="flex-1">
            <el-input v-model="accountLoginForm.captcha" autocomplete="off" :disabled="preview" placeholder="请输入验证码" :readonly="preview" />
          </el-form-item>
          <img :src="identifyCode" alt="验证码" class="w-35 h-10 cursor-pointer border" @click="refreshCaptcha" />
        </div>
        <el-form-item>
          <el-button :loading="isSubmitting" native-type="submit" type="primary" class="w-full">登录</el-button>
        </el-form-item>
      </el-form>
      <!-- 忘记密码 -->
      <el-button v-if="loginService.forgotPassword" size="default" class="mt-3" link type="primary" @click="loginService.forgotPassword()">
        忘记密码？
      </el-button>
    </div>
    <div v-if="accountLoginMethods.length" class="third-login flex-col-center gap-4">
      <el-divider>其他登录方式</el-divider>
      <div class="flex gap-4">
        <template v-for="method in accountLoginMethods" :key="method">
          <el-button circle size="large" class="text-xs! font-medium!" @click="selectLoginMethod(method)" v-if="loginMethod !== method">
            <MkIcon v-if="method === LOGIN_METHOD.LOCAL" name="icon_pc_outlined" :size="22.5" />
            <span v-else>{{ method }}</span>
          </el-button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.account-login.is-preview :deep(.el-input.is-disabled) {
  .el-input__wrapper {
    background-color: var(--el-fill-color-blank);
  }
}
</style>
