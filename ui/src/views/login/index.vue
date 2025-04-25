<template>
  <login-layout v-if="!loading" v-loading="loading">
    <LoginContainer :subTitle="user.themeInfo?.slogan || $t('theme.defaultSlogan')">
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
                :placeholder="$t('views.login.loginForm.username.placeholder')"
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
                :placeholder="$t('views.login.loginForm.password.placeholder')"
                show-password
              >
              </el-input>
            </el-form-item>
          </div>
          <div class="mb-24">
            <el-form-item prop="captcha">
              <div class="flex-between w-full">
                <el-input
                  size="large"
                  class="input-item"
                  v-model="loginForm.captcha"
                  :placeholder="$t('views.login.loginForm.captcha.placeholder')"
                >
                </el-input>

                <img :src="identifyCode" alt="" height="40" class="ml-8 cursor" @click="makeCode" />
              </div>
            </el-form-item>
          </div>
        </el-form>

        <el-button
          size="large"
          type="primary"
          class="w-full"
          @click="loginHandle"
          :loading="loading"
        >
          >{{ $t('views.login.buttons.login') }}
        </el-button>
        <div class="operate-container flex-between mt-12">
          <el-button
            :loading="loading"
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
import loginApi from '@/api/user/login'
import { t, getBrowserLang } from '@/locales'
import useStore from '@/stores'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { login, user } = useStore()
const { locale } = useI18n({ useScope: 'global' })
const loading = ref<boolean>(false)

const identifyCode = ref<string>('')

const loginFormRef = ref<FormInstance>()
const loginForm = ref<LoginRequest>({
  username: '',
  password: '',
  captcha: '',
})

const rules = ref<FormRules<LoginRequest>>({
  username: [
    {
      required: true,
      message: t('views.login.loginForm.username.requiredMessage'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: t('views.login.loginForm.password.requiredMessage'),
      trigger: 'blur',
    },
  ],
  captcha: [
    {
      required: true,
      message: t('views.login.loginForm.captcha.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

const loginHandle = () => {
  loginFormRef.value?.validate().then(() => {
    login.asyncLogin(loginForm.value, loading).then(() => {
      locale.value = localStorage.getItem('MaxKB-locale') || getBrowserLang() || 'en-US'
      router.push({ name: 'home' })
    })
  })
}
function makeCode() {
  loginApi.getCaptcha().then((res: any) => {
    identifyCode.value = res.data.captcha
  })
}
onBeforeMount(() => {
  makeCode()
})

onMounted(() => {})
</script>
<style lang="scss" scoped></style>
