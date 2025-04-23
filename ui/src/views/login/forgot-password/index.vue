<template>
  <login-layout v-if="!loading" v-loading="loading || sendLoading">
    <LoginContainer
      :subTitle="
        user.themeInfo?.slogan ? user.themeInfo?.slogan : $t('views.system.theme.defaultSlogan')
      "
    >
      <h2 class="mb-24">{{ $t('views.login.forgotPassword') }}</h2>
      <el-form
        class="register-form"
        ref="resetPasswordFormRef"
        :model="CheckEmailForm"
        :rules="rules"
      >
        <div class="mb-24">
          <el-form-item prop="email">
            <el-input
              size="large"
              class="input-item"
              v-model="CheckEmailForm.email"
              :placeholder="$t('views.user.userForm.form.email.placeholder')"
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="code">
            <div class="flex-between w-full">
              <el-input
                size="large"
                class="code-input"
                v-model="CheckEmailForm.code"
                :placeholder="$t('views.login.verificationCode.placeholder')"
              >
              </el-input>

              <el-button
                :disabled="isDisabled"
                size="large"
                class="send-email-button ml-12"
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
        </div>
      </el-form>
      <el-button size="large" type="primary" class="w-full" @click="checkCode"
        >{{ $t('views.login.buttons.checkCode') }}
      </el-button>
      <div class="operate-container mt-12">
        <el-button
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
import { onBeforeMount, ref } from 'vue'
import type { CheckCodeRequest } from '@/api/type/user'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import UserApi from '@/api/user'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'

const router = useRouter()
const { user } = useStore()

const CheckEmailForm = ref<CheckCodeRequest>({
  email: '',
  code: '',
  type: 'reset_password'
})

const resetPasswordFormRef = ref<FormInstance>()
const rules = ref<FormRules<CheckCodeRequest>>({
  email: [
    {
      required: true,
      message: t('views.user.userForm.form.email.requiredMessage'),
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        const emailRegExp = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
        if (!emailRegExp.test(value) && value != '') {
          callback(new Error(t('views.user.userForm.form.email.validatorEmail')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  code: [{ required: true, message: t('views.login.verificationCode.placeholder') }]
})
const loading = ref<boolean>(false)
const isDisabled = ref<boolean>(false)
const time = ref<number>(60)
const sendLoading = ref<boolean>(false)
const checkCode = () => {
  resetPasswordFormRef.value
    ?.validate()
    .then(() => UserApi.checkCode(CheckEmailForm.value, sendLoading))
    .then(() => router.push({ name: 'reset_password', params: CheckEmailForm.value }))
}
/**
 * 发送验证码
 */
const sendEmail = () => {
  resetPasswordFormRef.value?.validateField('email', (v: boolean) => {
    if (v) {
      UserApi.sendEmit(CheckEmailForm.value.email, 'reset_password', sendLoading).then(() => {
        MsgSuccess(t('views.login.verificationCode.successMessage'))
        isDisabled.value = true
        handleTimeChange()
      })
    }
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
onBeforeMount(() => {
  loading.value = true
  user.asyncGetProfile().then(() => {
    loading.value = false
  })
})
</script>
<style lang="scss" scoped></style>
