<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import JSEncrypt from 'jsencrypt'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormRules } from 'element-plus'
import ForgotPasswordApi from '@/api/admin/auth/forgot-password'
import LoginLayout from '../components/LoginLayout.vue'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

interface ForgotPasswordForm {
  confirmPassword: string
  email: string
  password: string
  verificationCode: string
}

const RESEND_WAIT_SECONDS = 60

defineOptions({ name: 'ForgotPasswordView' })

const router = useRouter()
const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

const forgotPasswordFormRef = ref<FormInstance>()
const forgotPasswordForm = reactive<ForgotPasswordForm>({ confirmPassword: '', email: '', password: '', verificationCode: '' })

const isSubmitting = ref(false)
const isSendingCode = ref(false)
const countdown = ref(0)
let countdownTimer: number | undefined
const isSendCodeDisabled = computed(() => !forgotPasswordForm.email.trim() || isSendingCode.value || countdown.value > 0)

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error(t('auth.fields.confirmPassword.requiredMessage')))
  } else if (value !== forgotPasswordForm.password) {
    callback(new Error(t('auth.fields.confirmPassword.mismatchMessage')))
  } else {
    callback()
  }
}

const forgotPasswordRules = computed<FormRules<ForgotPasswordForm>>(() => ({
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  email: [
    { whitespace: true, required: true, message: t('auth.fields.email.requiredMessage'), trigger: 'blur' },
    { type: 'email', message: t('auth.fields.email.invalidMessage'), trigger: 'blur' },
  ],
  password: [
    { required: true, message: t('auth.fields.password.requiredMessage'), trigger: 'blur' },
    { min: 6, max: 30, message: t('auth.forgotPassword.password.lengthMessage'), trigger: 'blur' },
  ],
  verificationCode: [{ whitespace: true, required: true, message: t('auth.fields.verificationCode.requiredMessage'), trigger: 'blur' }],
}))

const startCountdown = () => {
  countdown.value = RESEND_WAIT_SECONDS
  countdownTimer = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0 && countdownTimer) {
      window.clearInterval(countdownTimer)
      countdownTimer = undefined
    }
  }, 1000)
}

const handleSendCode = async () => {
  if (isSendingCode.value || countdown.value > 0 || !forgotPasswordFormRef.value) return

  await forgotPasswordFormRef.value.validateField('email', async (valid) => {
    if (!valid) return
    isSendingCode.value = true
    try {
      await ForgotPasswordApi.postSendVerificationCode(forgotPasswordForm.email)
      MsgSuccess(t('auth.forgotPassword.messages.codeSent'))
      startCountdown()
    } finally {
      isSendingCode.value = false
    }
  })
}

const handleResetPassword = async () => {
  if (!forgotPasswordFormRef.value) return

  await forgotPasswordFormRef.value.validate(async (valid) => {
    if (!valid) return
    isSubmitting.value = true
    try {
      if (!auth.baseProfile) {
        await auth.loadBaseProfile()
      }
      const encryptor = new JSEncrypt()
      encryptor.setPublicKey(auth.baseProfile?.rsa ?? '')
      const { confirmPassword: re_password, email, password, verificationCode: code } = forgotPasswordForm
      const encryptedData = encryptor.encrypt(JSON.stringify(password))
      if (!encryptedData) {
        return
      }
      const encryptedRePassword = encryptor.encrypt(JSON.stringify(re_password))
      if (!encryptedRePassword) {
        return
      }

      await ForgotPasswordApi.postResetPassword({ code, email, password: encryptedData, re_password: encryptedRePassword, encrypted: true })
      MsgSuccess(t('auth.forgotPassword.messages.passwordReset'))
      router.push({ name: 'login' })
    } finally {
      isSubmitting.value = false
    }
  })
}

onMounted(() => {
  void auth.loadBaseProfile()
})
</script>

<template>
  <LoginLayout>
    <!-- 返回登录页面 -->
    <el-button class="-mx-1" text @click="router.push({ name: 'login' })">
      <MkIcon name="icon_left_outlined" />
      <span>{{ t('auth.forgotPassword.actions.backToLogin') }}</span>
    </el-button>

    <h2 class="mt-4">{{ t('auth.forgotPassword.title') }}</h2>

    <el-form
      ref="forgotPasswordFormRef"
      :model="forgotPasswordForm"
      :rules="forgotPasswordRules"
      :validate-on-rule-change="false"
      class="mt-4"
      @submit.prevent="handleResetPassword"
      size="large"
    >
      <el-form-item prop="email">
        <el-input v-model="forgotPasswordForm.email" autocomplete="email" :placeholder="t('auth.fields.email.placeholder')" />
      </el-form-item>

      <el-form-item prop="verificationCode">
        <div class="flex w-full gap-3">
          <el-input v-model="forgotPasswordForm.verificationCode" :placeholder="t('auth.fields.verificationCode.placeholder')" />
          <!-- 发送邮箱验证码 -->
          <el-button plain class="min-w-35 shrink-0" :disabled="isSendCodeDisabled" :loading="isSendingCode" @click="handleSendCode">
            {{ countdown > 0 ? `${t('auth.forgotPassword.actions.resendCode')} (${countdown}s)` : t('auth.forgotPassword.actions.sendCode') }}
          </el-button>
        </div>
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="forgotPasswordForm.password"
          autocomplete="new-password"
          maxlength="30"
          :placeholder="t('auth.forgotPassword.password.placeholder')"
          show-password
          type="password"
        />
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input
          v-model="forgotPasswordForm.confirmPassword"
          autocomplete="new-password"
          maxlength="30"
          :placeholder="t('auth.fields.confirmPassword.placeholder')"
          show-password
          type="password"
        />
      </el-form-item>

      <!-- 提交密码重置 -->
      <el-button native-type="submit" type="primary" class="w-full" :loading="isSubmitting">{{ t('auth.forgotPassword.actions.submit') }}</el-button>
    </el-form>
  </LoginLayout>
</template>
