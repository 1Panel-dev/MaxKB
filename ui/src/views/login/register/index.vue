<template>
  <login-layout>
    <LoginContainer>
      <h4 class="mb-16">注册</h4>
      <el-form class="register-form" :model="registerForm" :rules="rules" ref="registerFormRef">
        <el-form-item prop="username">
          <el-input
            size="large"
            class="input-item"
            v-model="registerForm.username"
            placeholder="请输入用户名"
          >
            <template #prepend>
              <el-button :icon="UserFilled" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            type="password"
            size="large"
            class="input-item"
            v-model="registerForm.password"
            placeholder="请输入密码"
            show-password
          >
            <template #prepend>
              <el-button :icon="Lock" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="repassword">
          <el-input
            type="password"
            size="large"
            class="input-item"
            v-model="registerForm.re_password"
            placeholder="请输入确认密码"
            show-password
          >
            <template #prepend>
              <el-button :icon="Lock" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="email">
          <el-input
            size="large"
            class="input-item"
            v-model="registerForm.email"
            placeholder="请输入邮箱"
          >
            <template #prepend>
              <el-button :icon="Message" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="code">
          <div class="flex-between w-full">
            <el-input
              size="large"
              class="code-input"
              v-model="registerForm.code"
              placeholder="请输入验证码"
            >
              <template #prepend>
                <el-button :icon="Key" />
              </template>
            </el-input>
            <el-button
              size="large"
              class="send-email-button ml-16"
              @click="sendEmail"
              :loading="sendEmailLoading"
              >获取验证码</el-button
            >
          </div>
        </el-form-item>
      </el-form>
      <el-button type="primary" class="login-submit-button w-full" @click="register"
        >注册</el-button
      >
      <div class="operate-container mt-8">
        <el-button
          class="register"
          @click="router.push('/login')"
          link
          type="primary"
          icon="DArrowLeft"
        >
          返回登录
        </el-button>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { RegisterRequest } from '@/api/type/user'
import { UserFilled, Lock, Message, Key } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import UserApi from '@/api/user'
import { MsgSuccess } from '@/utils/message'
import type { FormInstance, FormRules } from 'element-plus'

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
      message: '请输入用户名',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 30,
      message: '长度在 6 到 30 个字符',
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: '请输入确认密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 30,
      message: '长度在 6 到 30 个字符',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (registerForm.value.password != registerForm.value.re_password) {
          callback(new Error('密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        const emailRegExp = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
        if (!emailRegExp.test(value) && value != '') {
          callback(new Error('请输入有效邮箱格式！'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  code: [{ required: true, message: '请输入验证码' }]
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
/**
 * 发送验证码
 */
const sendEmail = () => {
  registerFormRef.value?.validateField('email', (v: boolean) => {
    if (v) {
      UserApi.sendEmit(registerForm.value.email, 'register', sendEmailLoading).then(() => {
        MsgSuccess('发送验证码成功')
      })
    }
  })
}
</script>
<style lang="scss" scope>
@import '../index.scss';
</style>