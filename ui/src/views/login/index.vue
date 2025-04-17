<template>
  <login-layout v-if="!loading" v-loading="loading">
    <LoginContainer :subTitle="user.themeInfo?.slogan || $t('views.system.theme.defaultSlogan')">
      <h2 class="mb-24">{{ $t('views.login.title') }}</h2>
      <div>
        <el-form
          class="login-form"
          :rules="rules"
          :model="loginForm"
          ref="loginFormRef"
          @keyup.enter="login"
        >
          <div class="mb-24">
            <el-form-item prop="username">
              <el-input
                size="large"
                class="input-item"
                v-model="loginForm.username"
                :placeholder="$t('views.user.userForm.form.username.placeholder')"
              >
              </el-input>
            </el-form-item>
          </div>
          <div class="mb-24">
            <el-form-item prop="password">
              <el-input
                type="password"
                size="large"
                class="input-item"
                v-model="loginForm.password"
                :placeholder="$t('views.user.userForm.form.password.placeholder')"
                show-password
              >
              </el-input>
            </el-form-item>
          </div>
          <div class="mb-24">
            <el-form-item prop="code">
              <div class="flex-between w-full">
                <el-input
                  size="large"
                  class="input-item"
                  v-model="loginForm.code"
                  placeholder="请输入验证码"
                >
                </el-input>
                <VerifyCode v-model:code="identifyCode" />
              </div>
            </el-form-item>
          </div>
        </el-form>

        <el-button size="large" type="primary" class="w-full" @click="login"
          >{{ $t('views.login.buttons.login') }}
        </el-button>
        <div class="operate-container flex-between mt-12">
          <!-- <el-button class="register" @click="router.push('/register')" link type="primary">
          注册
        </el-button> -->
          <el-button
            class="forgot-password"
            @click="router.push('/forgot_password')"
            link
            type="primary"
          >
            {{ $t('views.login.forgotPassword') }}?
          </el-button>
        </div>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { onMounted, ref, onBeforeMount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import type { LoginRequest } from '@/api/type/login'
import LoginContainer from '@/views/login/components/LoginContainer.vue'
import LoginLayout from '@/views/login/components/LoginLayout.vue'
import VerifyCode from './components/VerifyCode.vue'
import { t, getBrowserLang } from '@/locales'
import useStore from '@/stores'

const router = useRouter()
const { user } = useStore()
// const { locale } = useI18n({ useScope: 'global' })
const loading = ref<boolean>(false)
const identifyCode = ref<string>('1234')

const loginFormRef = ref<FormInstance>()
const loginForm = ref<LoginRequest>({
  username: '',
  password: '',
  code: '',
})

const rules = ref<FormRules<LoginRequest>>({
  username: [
    {
      required: true,
      message: t('views.user.userForm.form.username.requiredMessage'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: t('views.user.userForm.form.password.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

// const modeList = ref<string[]>([''])
// const QrList = ref<any[]>([''])
// const loginMode = ref('')
// const showQrCodeTab = ref(false)

// interface qrOption {
//   key: string
//   value: string
// }

// const orgOptions = ref<qrOption[]>([])

const login = () => {
  //   loginFormRef.value?.validate().then(() => {
  //     loading.value = true
  //     user
  //       .login(loginMode.value, loginForm.value.username, loginForm.value.password)
  //       .then(() => {
  //         locale.value = localStorage.getItem('MaxKB-locale') || getBrowserLang() || 'en-US'
  //         router.push({ name: 'home' })
  //       })
  //       .finally(() => (loading.value = false))
  //   })
}

onBeforeMount(() => {
  // loading.value = true
})

onMounted(() => {})
</script>
<style lang="scss" scoped></style>
