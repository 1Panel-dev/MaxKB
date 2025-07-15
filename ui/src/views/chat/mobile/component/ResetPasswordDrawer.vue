<template>
  <el-drawer v-model="show" :with-header="false" class="reset-password-drawer" size="100%">
    <div class="navigation flex align-center mb-16">
      <el-icon size="16" @click="show = false">
        <ArrowLeftBold />
      </el-icon>
    </div>
    <h2 class="mb-16">{{ $t('views.login.resetPassword') }}</h2>

    <el-form ref="resetPasswordFormRef" :model="resetPasswordForm" :rules="rules">
      <el-form-item prop="password">
        <el-input
          type="password"
          size="large"
          v-model="resetPasswordForm.password"
          :placeholder="$t('views.login.loginForm.new_password.placeholder')"
          show-password
        >
        </el-input>
      </el-form-item>
      <el-form-item prop="re_password">
        <el-input
          type="password"
          size="large"
          v-model="resetPasswordForm.re_password"
          :placeholder="$t('views.login.loginForm.re_password.placeholder')"
          show-password
        >
        </el-input>
      </el-form-item>
    </el-form>
    <el-button type="primary" size="large" class="w-full" @click="resetPassword">{{
      $t('chat.confirmModification')
    }}</el-button>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { t } from '@/locales'
import type { ResetCurrentUserPasswordRequest } from '@/api/type/user'
import type { FormInstance, FormRules } from 'element-plus'
import useStore from '@/stores'
import chatAPI from '@/api/chat/chat'
import { useRouter } from 'vue-router'
import { MsgSuccess } from '@/utils/message'

const router = useRouter()
const { chatUser } = useStore()

const show = defineModel<boolean>('show', {
  required: true,
})

const resetPasswordFormRef = ref<FormInstance>()

const resetPasswordForm = ref<ResetCurrentUserPasswordRequest>({
  password: '',
  re_password: '',
})

const rules = ref<FormRules<ResetCurrentUserPasswordRequest>>({
  password: [
    {
      required: true,
      message: t('views.login.loginForm.new_password.placeholder'),
      trigger: 'blur',
    },
    {
      min: 6,
      max: 20,
      message: t('views.login.loginForm.password.lengthMessage'),
      trigger: 'blur',
    },
  ],
  re_password: [
    {
      required: true,
      message: t('views.login.loginForm.re_password.requiredMessage'),
      trigger: 'blur',
    },
    {
      min: 6,
      max: 20,
      message: t('views.login.loginForm.password.lengthMessage'),
      trigger: 'blur',
    },
    {
      validator: (rule, value, callback) => {
        if (resetPasswordForm.value.password != resetPasswordForm.value.re_password) {
          callback(new Error(t('views.login.loginForm.re_password.validatorMessage')))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
})

function resetPassword() {
  resetPasswordFormRef.value?.validate().then(() => {
    chatAPI.resetCurrentPassword(resetPasswordForm.value).then(() => {
      MsgSuccess(t('common.modifySuccess'))
      router.push({name: 'login'})
    })
  })
}
</script>

<style lang="scss">
.reset-password-drawer {
  .el-drawer__body {
    padding: 16px;
    padding-top: 0;
    background: #ffffff !important;

    .navigation {
      height: 44px;
    }
  }
}
</style>
