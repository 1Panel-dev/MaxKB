<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import LoginLayout from './components/LoginLayout.vue'

interface ForgotPasswordForm {
  confirmPassword: string
  email: string
  password: string
  verificationCode: string
}

defineOptions({ name: 'ForgotPasswordView' })

const router = useRouter()

const forgotPasswordFormRef = ref<FormInstance>()
const forgotPasswordForm = reactive<ForgotPasswordForm>({
  confirmPassword: '',
  email: '',
  password: '',
  verificationCode: '',
})

const validateConfirmPassword = (
  _rule: unknown,
  value: string,
  callback: (error?: Error) => void,
) => {
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

const handleResetPassword = async () => {
  if (!forgotPasswordFormRef.value) return

  await forgotPasswordFormRef.value.validate((valid) => {
    if (!valid) return
    // TODO: 接入忘记密码接口。
  })
}
</script>

<template>
  <LoginLayout>
    <el-button class="-mx-1" text @click="router.push({ name: 'login' })">
      <MkIcon name="icon_left_outlined" />
      <span>返回登录</span>
    </el-button>

    <h2 class="mt-4">修改密码</h2>

    <el-form
      ref="forgotPasswordFormRef"
      :model="forgotPasswordForm"
      :rules="forgotPasswordRules"
      class="mt-4"
      @submit.prevent="handleResetPassword"
      size="large"
    >
      <el-form-item prop="email">
        <el-input
          v-model="forgotPasswordForm.email"
          autocomplete="email"
          placeholder="请输入邮箱"
        />
      </el-form-item>

      <el-form-item prop="verificationCode">
        <div class="flex w-full gap-3">
          <el-input v-model="forgotPasswordForm.verificationCode" placeholder="请输入验证码" />
          <el-button plain class="w-35 shrink-0">获取验证码</el-button>
        </div>
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="forgotPasswordForm.password"
          autocomplete="new-password"
          maxlength="30"
          placeholder="请输入6-30位密码"
          show-password
          type="password"
        />
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input
          v-model="forgotPasswordForm.confirmPassword"
          autocomplete="new-password"
          maxlength="30"
          placeholder="请输入确认密码"
          show-password
          type="password"
        />
      </el-form-item>

      <el-button native-type="submit" type="primary" class="w-full">修改密码</el-button>
    </el-form>
  </LoginLayout>
</template>
