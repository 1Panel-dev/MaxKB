<template>
  <el-dialog
    v-model="resetPasswordDialog"
    :title="$t('views.login.resetPassword')"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      class="reset-password-form"
      ref="resetPasswordFormRef1"
      :model="resetPasswordForm"
      :rules="rules1"
    >
      <p class="mb-8 lighter">{{ $t('views.login.newPassword') }}</p>
      <el-form-item prop="password" style="margin-bottom: 8px">
        <el-input
          type="password"
          class="input-item"
          v-model="resetPasswordForm.password"
          :placeholder="$t('views.login.enterPassword')"
          show-password
        >
        </el-input>
      </el-form-item>
      <el-form-item prop="re_password">
        <el-input
          type="password"
          class="input-item"
          v-model="resetPasswordForm.re_password"
          :placeholder="$t('views.user.userForm.form.re_password.placeholder')"
          show-password
        >
        </el-input>
      </el-form-item>
    </el-form>
    <el-form
      class="reset-password-form mb-24"
      ref="resetPasswordFormRef2"
      :model="resetPasswordForm"
      :rules="rules2"
    >
      <p class="mb-8 lighter">{{ $t('views.login.useEmail') }}</p>
      <el-form-item style="margin-bottom: 8px">
        <el-input
          class="input-item"
          :disabled="true"
          v-bind:modelValue="user.userInfo?.email"
          :placeholder="t('views.user.userForm.form.email.placeholder')"
        >
        </el-input>
      </el-form-item>
      <el-form-item prop="code">
        <div class="flex-between w-full">
          <el-input
            class="code-input"
            v-model="resetPasswordForm.code"
            :placeholder="$t('views.login.verificationCode.placeholder')"
          >
          </el-input>
          <el-button
            :disabled="isDisabled"
            class="send-email-button ml-8"
            @click="sendEmail"
            :loading="loading"
          >
            {{
              isDisabled
                ? `${$t('views.login.verificationCode.resend')}（${time}s）`
                : $t('views.login.verificationCode.getVerificationCode')
            }}
          </el-button>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="resetPasswordDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="resetPassword">
          {{ $t('common.save') }}
        </el-button>
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

const resetPasswordFormRef1 = ref<FormInstance>()
const resetPasswordFormRef2 = ref<FormInstance>()

const loading = ref<boolean>(false)
const isDisabled = ref<boolean>(false)
const time = ref<number>(60)

const rules1 = ref<FormRules<ResetCurrentUserPasswordRequest>>({
  password: [
    {
      required: true,
      message: t('views.login.enterPassword'),
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
const rules2 = ref<FormRules<ResetCurrentUserPasswordRequest>>({
  // @ts-ignore
  code: [
    {
      required: true,
      message: t('views.login.verificationCode.placeholder'),
      trigger: 'blur'
    }
  ]
})
/**
 * 发送验证码
 */
const sendEmail = () => {
  resetPasswordFormRef1.value?.validate().then(() => {
    UserApi.sendEmailToCurrent(loading).then(() => {
      MsgSuccess(t('views.login.verificationCode.successMessage'))
      isDisabled.value = true
      handleTimeChange()
    })
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
  resetPasswordFormRef1.value?.resetFields()
  resetPasswordFormRef2.value?.resetFields()
}
const resetPassword = () => {
  resetPasswordFormRef1.value?.validate().then(() => {
    resetPasswordFormRef2.value
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
  })
}
const close = () => {
  resetPasswordDialog.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scope></style>
