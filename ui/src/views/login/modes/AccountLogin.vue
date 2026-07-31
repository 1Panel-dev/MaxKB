<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { AccountLoginForm, LoginMethod, LoginOption } from '../types'

defineOptions({ name: 'AccountLogin' })

const emit = defineEmits<{
  'select-method': [method: LoginMethod]
}>()

withDefaults(
  defineProps<{
    loginMethods?: LoginOption<LoginMethod>[]
  }>(),
  {
    loginMethods: () => [],
  },
)

const accountLoginFormRef = ref<FormInstance>()
const accountLoginForm = reactive<AccountLoginForm>({
  captcha: '',
  password: '',
  username: '',
})

const accountLoginRules: FormRules<AccountLoginForm> = {
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!accountLoginFormRef.value) return

  await accountLoginFormRef.value.validate((valid) => {
    if (!valid) return
  })
}
</script>

<template>
  <h2 class="mb-4">账号登录</h2>

  <el-form
    ref="accountLoginFormRef"
    :model="accountLoginForm"
    :rules="accountLoginRules"
    class="login-form"
    @submit.prevent="handleLogin"
    size="large"
  >
    <el-form-item prop="username">
      <el-input
        v-model="accountLoginForm.username"
        autocomplete="username"
        placeholder="请输入用户名"
      />
    </el-form-item>
    <el-form-item prop="password">
      <el-input
        v-model="accountLoginForm.password"
        autocomplete="current-password"
        placeholder="请输入密码"
        show-password
        type="password"
      />
    </el-form-item>
    <!-- <div class="verification-row">
      <el-form-item prop="captcha">
        <el-input v-model="accountLoginForm.captcha" placeholder="请输入验证码" />
      </el-form-item>
      <button type="button" class="captcha-image" aria-label="刷新验证码">验证码</button>
    </div> -->

    <el-button native-type="submit" type="primary" size="large" class="w-full">登录</el-button>

    <RouterLink :to="{ name: 'forgot-password' }" class="forgot-password"> 忘记密码？ </RouterLink>
  </el-form>

  <div v-if="loginMethods.length" class="alternative-login">
    <p>其他登录方式</p>
    <div class="alternative-login-options">
      <el-button
        v-for="method in loginMethods"
        :key="method.value"
        @click="emit('select-method', method.value)"
      >
        {{ method.label }}
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
