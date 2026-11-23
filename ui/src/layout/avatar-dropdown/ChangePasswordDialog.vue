<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import JSEncrypt from 'jsencrypt'
import { useI18n } from 'vue-i18n'
import type { UpdatePasswordForm } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import { useStore } from '@/stores'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ChangePasswordDialog' })

const { t } = useI18n({ useScope: 'global' })

const router = useRouter()
const { auth } = useStore()

const dialogVisible = ref(false)
const passwordSubmitting = ref(false)

// 当前账号密码表单与校验。
const userPasswordFormRef = ref<FormInstance>()
const userPasswordForm = reactive<UpdatePasswordForm>({ password: '', re_password: '' })

function validateConfirmPassword(_rule: unknown, value: string, callback: (error?: Error) => void) {
  if (!value) {
    callback(new Error(t('user.confirmPassword.requiredMessage')))
  } else if (value !== userPasswordForm.password) {
    callback(new Error(t('user.confirmPassword.mismatchMessage')))
  } else {
    callback()
  }
}

const userPasswordRules = computed<FormRules<UpdatePasswordForm>>(() => ({
  password: [
    { required: true, message: t('user.password.requiredMessage'), trigger: 'blur' },
    { min: 6, max: 20, message: t('common.validation.lengthRange', { min: 6, max: 20 }), trigger: 'blur' },
  ],
  re_password: [
    { required: true, whitespace: true, message: t('user.confirmPassword.requiredMessage'), trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}))

function open() {
  dialogVisible.value = true
}

// 加密提交成功后，服务端会使当前登录凭据失效。
function submitPassword() {
  if (passwordSubmitting.value) return
  userPasswordFormRef.value?.validate((valid) => {
    if (!valid) return
    passwordSubmitting.value = true
    const encryptor = new JSEncrypt()
    encryptor.setPublicKey(auth.baseProfile?.rsa ?? '')
    const encryptedData = encryptor.encrypt(JSON.stringify(userPasswordForm))
    if (!encryptedData) {
      passwordSubmitting.value = false
      MsgError(t('auth.changePassword.encryptionFailedMessage'))
      return
    }

    return CurrentUserApi.postCurrentUserPassword({ encryptedData })
      .then(() => {
        MsgSuccess(t('auth.changePassword.successMessage'))
        auth.clearToken()
        dialogVisible.value = false
        return router.push({ name: 'login' }).then(() => undefined)
      })
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
      :disabled="passwordSubmitting"
      :rules="userPasswordRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('user.password.label')" prop="password">
        <el-input
          v-model="userPasswordForm.password"
          autocomplete="new-password"
          maxlength="20"
          :placeholder="t('user.password.placeholder')"
          show-password
          type="password"
        />
      </el-form-item>
      <el-form-item :label="t('user.confirmPassword.label')" prop="re_password">
        <el-input
          v-model="userPasswordForm.re_password"
          autocomplete="new-password"
          maxlength="20"
          :placeholder="t('user.confirmPassword.placeholder')"
          show-password
          type="password"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消修改密码 -->
      <el-button :disabled="passwordSubmitting" plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存新密码 -->
      <el-button :loading="passwordSubmitting" type="primary" @click="submitPassword">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
