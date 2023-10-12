<template>
  <login-layout v-loading="loading">
    <LoginContainer subTitle="欢迎使用智能客服管理平台">
      <el-form class="login-form" :rules="rules" :model="loginForm" ref="loginFormRef">
        <el-form-item>
          <el-input
            size="large"
            class="input-item"
            v-model="loginForm.username"
            placeholder="请输入用户名"
          >
            <template #prepend>
              <el-button icon="UserFilled" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-input
            type="password"
            size="large"
            class="input-item"
            v-model="loginForm.password"
            placeholder="请输入密码"
            show-password
          >
            <template #prepend>
              <el-button icon="Lock" />
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <div class="operate-container flex-between">
        <el-button class="register" @click="router.push('/register')" link type="primary">
          注册
        </el-button>
        <el-button
          class="forgot-password"
          @click="router.push('/forgot_password')"
          link
          type="primary"
        >
          忘记密码
        </el-button>
      </div>
      <el-button type="primary" class="login-submit-button w-full" @click="login">登录</el-button>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { LoginRequest } from '@/api/user/type'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'

const loading = ref<boolean>(false)
const userStore = useUserStore()
const router = useRouter()
const loginForm = ref<LoginRequest>({
  username: '',
  password: ''
})

const rules = ref<FormRules<LoginRequest>>({
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
  ]
})
const loginFormRef = ref<FormInstance>()

const login = () => {
  loginFormRef.value?.validate().then(() => {
    loading.value = true
    userStore
      .login(loginForm.value.username, loginForm.value.password)
      .then(() => {
        router.push({ name: 'home' })
      })
      .finally(() => (loading.value = false))
  })
}
</script>
<style lang="scss" scope>
@import './index.scss';
</style>
