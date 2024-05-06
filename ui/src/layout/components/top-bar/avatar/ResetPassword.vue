<template>
  <el-dialog v-model="resetPasswordDialog" :title="$t('layout.topbar.avatar.resetPassword')">
    <el-form
      class="reset-password-form mb-24"
      ref="resetPasswordFormRef"
      :model="resetPasswordForm"
      :rules="rules"
    >
      <p class="mb-8 lighter">{{ $t("layout.topbar.avatar.dialog.newPassword") }}</p>
      <el-form-item prop="password" style="margin-bottom: 8px">
        <el-input
          type="password"
          class="input-item"
          v-model="resetPasswordForm.password"
          :placeholder="$t('layout.topbar.avatar.dialog.enterPassword')"
          show-password
        >
        </el-input>
      </el-form-item>
      <el-form-item prop="re_password">
        <el-input
          type="password"
          class="input-item"
          v-model="resetPasswordForm.re_password"
          :placeholder="$t('layout.topbar.avatar.dialog.confirmPassword')"
          show-password
        >
        </el-input>
      </el-form-item>
      <p class="mb-8 lighter">{{ $t("layout.topbar.avatar.dialog.useEmail") }}</p>
      <el-form-item style="margin-bottom: 8px">
        <el-input
          class="input-item"
          :disabled="true"
          v-bind:modelValue="user.userInfo?.email"
          :placeholder="$t('layout.topbar.avatar.dialog.enterEmail')"
        >
        </el-input>
      </el-form-item>
      <el-form-item prop="code">
        <div class="flex-between w-full">
          <el-input class="code-input" v-model="resetPasswordForm.code" :placeholder="$t('layout.topbar.avatar.dialog.enterVerificationCode')">
          </el-input>
          <el-button
            :disabled="isDisabled"
            class="send-email-button ml-8"
            @click="sendEmail"
            :loading="loading"
          >
            {{ isDisabled ? $t('layout.topbar.avatar.dialog.resend', { time }) : $t('layout.topbar.avatar.dialog.getVerificationCode') }}
          </el-button>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="resetPasswordDialog = false">{{ $t('layout.topbar.avatar.dialog.cancel') }}</el-button>
        <el-button type="primary" @click="resetPassword"> {{ $t('layout.topbar.avatar.dialog.save') }} </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { ResetCurrentUserPasswordRequest } from '@/api/type/user'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import UserApi from '@/api/user'
import useStore from '@/stores'
import { useRouter } from 'vue-router'
import { t } from '@/locales'
const router = useRouter()
const { user } = useStore()

const resetPasswordDialog = ref<boolean>(false)

const resetPasswordForm = ref<ResetCurrentUserPasswordRequest>({
  code: '',
  password: '',
  re_password: ''
})

const resetPasswordFormRef = ref<FormInstance>()

const loading = ref<boolean>(false)
const isDisabled = ref<boolean>(false)
const time = ref<number>(60)

const rules = ref<FormRules<ResetCurrentUserPasswordRequest>>({
  // @ts-ignore
  code: [{ required: true, message: t('layout.topbar.avatar.dialog.enterVerificationCode'), trigger: 'blur' }],
  password: [
    {
      required: true,
      message: t('layout.topbar.avatar.dialog.enterPassword'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('layout.topbar.avatar.dialog.passwordLength'),
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: t('layout.topbar.avatar.dialog.confirmPassword'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('layout.topbar.avatar.dialog.passwordLength'),
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (resetPasswordForm.value.password != resetPasswordForm.value.re_password) {
          callback(new Error(t('layout.topbar.avatar.dialog.passwordMismatch')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})
/**
 * 发送验证码
 */
const sendEmail = () => {
  UserApi.sendEmailToCurrent(loading).then(() => {
    MsgSuccess(t('verificationCodeSentSuccess'))
    isDisabled.value = true
    handleTimeChange()
  })
}

const handleTimeChange = () => {
  if (time.value <= 0) {
    isDisabled.value = false
    time.value = 60
  } else {
    setTimeout(() => {
      time.value--
      handleTimeChange()
    }, 1000)
  }
}

const open = () => {
  resetPasswordForm.value = {
    code: '',
    password: '',
    re_password: ''
  }
  resetPasswordDialog.value = true
  resetPasswordFormRef.value?.resetFields()
}
const resetPassword = () => {
  resetPasswordFormRef.value
    ?.validate()
    .then(() => {
      return UserApi.resetCurrentUserPassword(resetPasswordForm.value)
    })
    .then(() => {
      return user.logout()
    })
    .then(() => {
      router.push({ name: 'login' })
    })
}
const close = () => {
  resetPasswordDialog.value = false
}

defineExpose({ open, close })


</script>
<style lang="scss" scope></style>
