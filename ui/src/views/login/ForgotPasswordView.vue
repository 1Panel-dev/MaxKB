<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import LoginLayout from './components/LoginLayout.vue'
import type { ForgotPasswordForm } from './types'

defineOptions({ name: 'ForgotPasswordView' })

const forgotPasswordFormRef = ref<FormInstance>()
const forgotPasswordForm = reactive<ForgotPasswordForm>({
  email: '',
  verificationCode: '',
})

const forgotPasswordRules: FormRules<ForgotPasswordForm> = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' },
  ],
  verificationCode: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

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
    <h1>忘记密码</h1>
    <p class="mt-2 text-N600">验证您的邮箱后重新设置登录密码</p>

    <el-form
      ref="forgotPasswordFormRef"
      :model="forgotPasswordForm"
      :rules="forgotPasswordRules"
      class="mt-8"
      @submit.prevent="handleResetPassword"
    >
      <el-form-item prop="email">
        <el-input
          v-model="forgotPasswordForm.email"
          autocomplete="email"
          placeholder="请输入邮箱"
        />
      </el-form-item>

      <div class="grid grid-cols-[1fr_120px] gap-3">
        <el-form-item prop="verificationCode">
          <el-input v-model="forgotPasswordForm.verificationCode" placeholder="邮箱验证码" />
        </el-form-item>
        <el-button>获取验证码</el-button>
      </div>

      <el-button native-type="submit" type="primary" class="w-full">下一步</el-button>
    </el-form>

    <RouterLink :to="{ name: 'login' }" class="mt-4 inline-block text-primary">
      返回登录
    </RouterLink>
  </LoginLayout>
</template>
