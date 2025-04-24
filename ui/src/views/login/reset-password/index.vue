<template>
  <login-layout v-if="!loading" v-loading="loading || sendLoading">
    <LoginContainer
      :subTitle="
        user.themeInfo?.slogan ? user.themeInfo?.slogan : $t('views.system.theme.defaultSlogan')
      "
    >
      <h2 class="mb-24">{{ $t('views.login.resetPassword') }}</h2>
      <el-form
        class="reset-password-form"
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="rules"
      >
        <div class="mb-24">
          <el-form-item prop="password">
            <el-input
              type="password"
              size="large"
              class="input-item"
              v-model="resetPasswordForm.password"
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
              v-model="resetPasswordForm.re_password"
              :placeholder="$t('views.user.userForm.form.re_password.placeholder')"
              show-password
            >
            </el-input>
          </el-form-item>
        </div>
      </el-form>
      <el-button size="large" type="primary" class="w-full" @click="resetPassword"
        >{{ $t('common.confirm') }}
      </el-button>
      <div class="operate-container mt-12">
        <el-button
          size="large"
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
import { ref, onMounted, onBeforeMount } from 'vue'
import type { ResetPasswordRequest } from '@/api/type/user'
import { useRouter, useRoute } from 'vue-router'
import { MsgSuccess } from '@/utils/message'
import type { FormInstance, FormRules } from 'element-plus'
import UserApi from '@/api/user'
import { t } from '@/locales'
import useStore from '@/stores'

const { user } = useStore()
const router = useRouter()
const route = useRoute()
const {
  params: { code, email }
} = route
const resetPasswordForm = ref<ResetPasswordRequest>({
  password: '',
  re_password: '',
  email: '',
  code: ''
})

onMounted(() => {
  if (code && email) {
    resetPasswordForm.value.code = code as string
    resetPasswordForm.value.email = email as string
  } else {
    router.push('forgot_password')
  }
})
onBeforeMount(() => {
  loading.value = true
  user.asyncGetProfile().then(() => {
    loading.value = false
  })
})
const rules = ref<FormRules<ResetPasswordRequest>>({
  password: [
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
        if (resetPasswordForm.value.password != resetPasswordForm.value.re_password) {
          callback(new Error(t('views.user.userForm.form.re_password.validatorMessage')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})
const resetPasswordFormRef = ref<FormInstance>()
const loading = ref<boolean>(false)
const sendLoading = ref<boolean>(false)
const resetPassword = () => {
  resetPasswordFormRef.value
    ?.validate()
    .then(() => UserApi.resetPassword(resetPasswordForm.value, sendLoading))
    .then(() => {
      MsgSuccess(t('common.modifySuccess'))
      router.push({ name: 'login' })
    })
}
</script>
<style lang="scss" scoped></style>
