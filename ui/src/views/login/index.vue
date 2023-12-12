<template>
  <login-layout v-loading="loading">
    <LoginContainer subTitle="欢迎使用 MaxKB 管理平台">
      <h2 class="mb-24">普通登录</h2>
      <el-form class="login-form" :rules="rules" :model="loginForm" ref="loginFormRef">
        <el-form-item prop="username">
          <el-input
            size="large"
            class="input-item"
            v-model="loginForm.username"
            placeholder="请输入用户名"
          >
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            type="password"
            size="large"
            class="input-item"
            v-model="loginForm.password"
            placeholder="请输入密码"
            show-password
          >
          </el-input>
        </el-form-item>
      </el-form>
      <el-button type="primary" class="login-submit-button mt-4 w-full" @click="login"
        >登录</el-button
      >
      <div class="operate-container flex-between mt-12">
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
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { LoginRequest } from '@/api/type/user'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import useStore from '@/stores'

const loading = ref<boolean>(false)
const { user } = useStore()
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
      max: 20,
      message: '长度在 6 到 20 个字符',
      trigger: 'blur'
    }
  ]
})
const loginFormRef = ref<FormInstance>()

const login = () => {
  loginFormRef.value?.validate().then(() => {
    loading.value = true
    user
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
