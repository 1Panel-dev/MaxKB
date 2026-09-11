<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import JSEncrypt from 'jsencrypt'
import type { FormInstance, FormRules } from 'element-plus'
import ForgotPasswordApi from '@/api/admin/auth/forgot-password'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import LoginLayout from './components/LoginLayout.vue'

interface ForgotPasswordForm {
  confirmPassword: string
  email: string
  password: string
  verificationCode: string
}

const RESEND_WAIT_SECONDS = 60

defineOptions({ name: 'ForgotPasswordView' })

const router = useRouter()
const { auth } = useStore()

const forgotPasswordFormRef = ref<FormInstance>()
const forgotPasswordForm = reactive<ForgotPasswordForm>({ confirmPassword: '', email: '', password: '', verificationCode: '' })

const isSubmitting = ref(false)
const isSendingCode = ref(false)
const countdown = ref(0)
let countdownTimer: number | undefined

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请输入确认密码'))
  } else if (value !== forgotPasswordForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const forgotPasswordRules = reactive<FormRules<ForgotPasswordForm>>({
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度应为 6-30 位', trigger: 'blur' },
  ],
  verificationCode: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
})

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
      MsgSuccess('验证码已发送，请查收邮件')
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
      const encryptedData = encryptor.encrypt(JSON.stringify({ password, re_password }))
      if (!encryptedData) {
        return
      }

      await ForgotPasswordApi.postResetPassword({ code, email, password: encryptedData, re_password: encryptedData, encrypted: true })
      MsgSuccess('密码修改成功，请使用新密码登录')
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
    <el-button class="-mx-1" text @click="router.push({ name: 'login' })">
      <MkIcon name="icon_left_outlined" />
      <span>返回登录</span>
    </el-button>

    <h2 class="mt-4">修改密码</h2>

    <el-form ref="forgotPasswordFormRef" :model="forgotPasswordForm" :rules="forgotPasswordRules" class="mt-4" @submit.prevent="handleResetPassword" size="large">
      <el-form-item prop="email">
        <el-input v-model="forgotPasswordForm.email" autocomplete="email" placeholder="请输入邮箱" />
      </el-form-item>

      <el-form-item prop="verificationCode">
        <div class="flex w-full gap-3">
          <el-input v-model="forgotPasswordForm.verificationCode" placeholder="请输入验证码" />
          <el-button plain class="w-35 shrink-0" :disabled="countdown > 0" :loading="isSendingCode" @click="handleSendCode">
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </el-button>
        </div>
      </el-form-item>

      <el-form-item prop="password">
        <el-input v-model="forgotPasswordForm.password" autocomplete="new-password" maxlength="30" placeholder="请输入6-30位密码" show-password type="password" />
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input v-model="forgotPasswordForm.confirmPassword" autocomplete="new-password" maxlength="30" placeholder="请输入确认密码" show-password type="password" />
      </el-form-item>

      <el-button native-type="submit" type="primary" class="w-full" :loading="isSubmitting">修改密码</el-button>
    </el-form>
  </LoginLayout>
</template>
