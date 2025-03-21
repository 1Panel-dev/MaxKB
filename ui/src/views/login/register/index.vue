<template>
  <login-layout>
    <LoginContainer :subTitle="$t('views.system.theme.defaultSlogan')">
      <h2 class="mb-24">{{ $t('views.login.userRegister') }}</h2>
      <el-form class="register-form" :model="registerForm" :rules="rules" ref="registerFormRef">
        <div class="mb-24">
          <el-form-item prop="username">
            <el-input
              size="large"
              class="input-item"
              v-model="registerForm.username"
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
              v-model="registerForm.password"
              :placeholder="$t('views.user.userForm.form.password.placeholder')"
              show-password
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="re_password">
            <el-input
              type="password"
              size="large"
              class="input-item"
              v-model="registerForm.re_password"
              :placeholder="$t('views.user.userForm.form.re_password.placeholder')"
              show-password
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="email">
            <el-input
              size="large"
              class="input-item"
              v-model="registerForm.email"
              :placeholder="$t('views.user.userForm.form.email.placeholder')"
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="code">
            <div class="flex-between w-full">
              <el-input
                size="large"
                class="code-input"
                v-model="registerForm.code"
                :placeholder="$t('views.login.verificationCode.placeholder')"
              >
              </el-input>
              <el-button
                :disabled="isDisabled"
                size="large"
                class="send-email-button ml-12"
                @click="sendEmail"
                :loading="sendEmailLoading"
              >
                {{
                  isDisabled
                    ? `${$t('views.login.verificationCode.resend')}（${time}s）`
                    : $t('views.login.verificationCode.getVerificationCode')
                }}</el-button
              >
            </div>
          </el-form-item>
        </div>
      </el-form>
      <el-button size="large" type="primary" class="w-full" @click="register">{{
        $t('views.login.buttons.register')
      }}</el-button>
      <div class="operate-container mt-12">
        <el-button
          class="register"
          @click="router.push('/login')"
          link
          type="primary"
          icon="ArrowLeft"
        >
          {{ $t('views.login.buttons.backLogin') }}
        </el-button>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { RegisterRequest } from '@/api/type/user'
import { useRouter } from 'vue-router'
import UserApi from '@/api/user'
import { MsgSuccess } from '@/utils/message'
import type { FormInstance, FormRules } from 'element-plus'
import { t } from '@/locales'
const router = useRouter()
const registerForm = ref<RegisterRequest>({
  username: '',
  password: '',
  re_password: '',
  email: '',
  code: ''
})

const rules = ref<FormRules<RegisterRequest>>({
  username: [
    {
      required: true,
      message: t('views.user.userForm.form.username.placeholder'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('views.user.userForm.form.username.lengthMessage'),
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: t('views.user.userForm.form.password.requiredMessage'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('views.user.userForm.form.password.lengthMessage'),
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: t('views.user.userForm.form.re_password.requiredMessage'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('views.user.userForm.form.password.lengthMessage'),
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (registerForm.value.password != registerForm.value.re_password) {
          callback(new Error(t('views.user.userForm.form.password.validatorMessage')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    {
      required: true,
      message: t('views.user.userForm.form.email.requiredMessage'),
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        const emailRegExp = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
        if (!emailRegExp.test(value) && value != '') {
          callback(new Error(t('views.user.userForm.form.email.validatorEmail')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  code: [{ required: true, message: t('views.login.verificationCode.placeholder') }]
})

const registerFormRef = ref<FormInstance>()
const register = () => {
  registerFormRef.value
    ?.validate()
    .then(() => {
      return UserApi.register(registerForm.value)
    })
    .then(() => {
      router.push('login')
    })
}
const sendEmailLoading = ref<boolean>(false)
const isDisabled = ref<boolean>(false)
const time = ref<number>(60)
/**
 * 发送验证码
 */
const sendEmail = () => {
  registerFormRef.value?.validateField('email', (v: boolean) => {
    if (v) {
      UserApi.sendEmit(registerForm.value.email, 'register', sendEmailLoading).then(() => {
        MsgSuccess(t('views.login.verificationCode.successMessage'))
        isDisabled.value = true
        handleTimeChange()
      })
    }
  })
}
const handleTimeChange = () => {
  if (time.value <= 0) {
    isDisabled.value = false
    time.value = 60
  } else {
    setTimeout(() => {
      time.value--
      handleTimeChange()
    }, 1000)
  }
}
</script>
<style lang="scss" scoped></style>
