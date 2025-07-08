<template>
  <el-dialog
    v-model="resetPasswordDialog"
    :title="$t('views.login.resetPassword')"
    destroy-on-close
    append-to-body
    align-center
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
          :placeholder="$t('views.login.enterPassword')"
          show-password
        >
        </el-input>
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
import UserApi from '@/api/user/user'
import useStore from '@/stores'
import { useRouter } from 'vue-router'
import { t } from '@/locales'

const props = defineProps<{
  emitConfirm?: boolean // 在父级调接口
}>()

const emit = defineEmits<{
  (e: 'confirm', value: ResetCurrentUserPasswordRequest): void
}>()

const router = useRouter()
const { login } = useStore()

const resetPasswordDialog = ref<boolean>(false)

const resetPasswordForm = ref<ResetCurrentUserPasswordRequest>({
  code: '',
  password: '',
  re_password: '',
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
    //code: '',
    password: '',
    re_password: '',
  }
  resetPasswordDialog.value = true
  resetPasswordFormRef1.value?.resetFields()
  resetPasswordFormRef2.value?.resetFields()
}
const resetPassword = () => {
  resetPasswordFormRef1.value?.validate().then(() => {
    if (props.emitConfirm) {
      emit('confirm', resetPasswordForm.value)
    } else {
      return UserApi.resetCurrentPassword(resetPasswordForm.value).then(() => {
        login.logout()
        router.push({ name: 'login' })
      })
    }
  })
}
const close = () => {
  resetPasswordDialog.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scope></style>
