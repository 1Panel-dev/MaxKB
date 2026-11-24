<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import JSEncrypt from 'jsencrypt'
import { useI18n } from 'vue-i18n'
import type { UpdatePasswordForm } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserApi from '@/api/chat/chat-user'
import { useStore } from '@/stores/chat'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'UserPwdDialog' })

const { t } = useI18n({ useScope: 'global' })
const router = useRouter()
const { auth } = useStore()

const dialogVisible = ref(false)
const passwordSubmitting = ref(false)

const userPasswordFormRef = ref<FormInstance>()
const userPasswordForm = reactive<UpdatePasswordForm>({ password: '', re_password: '' })

function validateConfirmPassword(_rule: unknown, value: string, callback: (error?: Error) => void) {
  if (!value) {
    callback(new Error(t('auth.changePassword.confirmPassword.requiredMessage')))
  } else if (value !== userPasswordForm.password) {
    callback(new Error(t('auth.changePassword.confirmPassword.mismatchMessage')))
  } else {
    callback()
  }
}

const userPasswordRules = computed<FormRules<UpdatePasswordForm>>(() => ({
  password: [
    { required: true, whitespace: true, message: t('auth.changePassword.newPassword.requiredMessage'), trigger: 'blur' },
    { min: 6, max: 20, message: t('common.validation.lengthRange', { min: 6, max: 20 }), trigger: 'blur' },
  ],
  re_password: [{ required: true, whitespace: true, validator: validateConfirmPassword, trigger: 'blur' }],
}))

function open() {
  dialogVisible.value = true
}

async function submitPassword() {
  if (passwordSubmitting.value) return
  userPasswordFormRef.value?.validate((valid) => {
    if (!valid) return
    passwordSubmitting.value = true
    const encryptor = new JSEncrypt()
    encryptor.setPublicKey(auth.authProfile?.rsa_key ?? '')
    const encryptedData = encryptor.encrypt(JSON.stringify(userPasswordForm))
    if (!encryptedData) {
      MsgError(t('auth.changePassword.chatEncryptionFailedMessage'))
      passwordSubmitting.value = false
      return
    }

    return ChatUserApi.postResetPassword({ encryptedData }, auth.accessToken)
      .then(() => {
        MsgSuccess(t('user.password.changeSuccess'))

        dialogVisible.value = false
        auth.clearToken()
        return router.replace({ path: router.currentRoute.value.fullPath, force: true }).then(() => undefined)
      })
      .catch(() => {})
      .finally(() => {
        passwordSubmitting.value = false
      })
  })
}

function resetData() {
  Object.assign(userPasswordForm, { password: '', re_password: '' })
  passwordSubmitting.value = false
  userPasswordFormRef.value?.clearValidate()
}
defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('auth.changePassword.title')" @closed="resetData">
    <el-form
      ref="userPasswordFormRef"
      :model="userPasswordForm"
      :rules="userPasswordRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('auth.changePassword.newPassword.label')" prop="password">
        <el-input
          v-model="userPasswordForm.password"
          autocomplete="new-password"
          maxlength="20"
          :placeholder="t('auth.changePassword.newPassword.placeholder')"
          show-password
          type="password"
        />
      </el-form-item>
      <el-form-item :label="t('auth.changePassword.confirmPassword.label')" prop="re_password">
        <el-input
          v-model="userPasswordForm.re_password"
          autocomplete="new-password"
          maxlength="20"
          :placeholder="t('auth.changePassword.confirmPassword.placeholder')"
          show-password
          type="password"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消修改密码 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存新密码 -->
      <el-button :loading="passwordSubmitting" type="primary" @click="submitPassword">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
