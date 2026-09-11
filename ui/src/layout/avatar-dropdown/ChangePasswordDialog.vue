<script setup lang="ts">
import { reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import CurrentUserApi from '@/api/admin/auth/current-user'
import type { UpdatePasswordForm } from '@/api/types'
import { useStore } from '@/stores'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ChangePasswordDialog' })

const router = useRouter()
const { auth } = useStore()

const dialogVisible = ref(false)
const passwordSubmitting = ref(false)

// 当前账号密码表单与校验。
const userPasswordFormRef = ref<FormInstance>()
const userPasswordForm = reactive<UpdatePasswordForm>({ password: '', re_password: '' })

function validateConfirmPassword(_rule: unknown, value: string, callback: (error?: Error) => void) {
  if (!value) {
    callback(new Error('请输入确认密码'))
  } else if (value !== userPasswordForm.password) {
    callback(new Error('输入的密码不一致'))
  } else {
    callback()
  }
}

const userPasswordRules = reactive<FormRules<UpdatePasswordForm>>({
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度应为 6-20 个字符', trigger: 'blur' },
  ],
  re_password: [{ validator: validateConfirmPassword, trigger: 'blur' }],
})

function open() {
  resetData()
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
      MsgError('密码加密失败，请刷新页面后重试')
      return
    }

    return CurrentUserApi.postCurrentUserPassword({ encryptedData })
      .then(() => {
        MsgSuccess('密码修改成功，请重新登录')
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
  <MkDialog v-model="dialogVisible" title="修改密码" :show-close="!passwordSubmitting" @closed="resetData">
    <el-form
      ref="userPasswordFormRef"
      :model="userPasswordForm"
      :disabled="passwordSubmitting"
      :rules="userPasswordRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="新密码" prop="password">
        <el-input
          v-model="userPasswordForm.password"
          autocomplete="new-password"
          maxlength="20"
          placeholder="请输入新密码"
          show-password
          type="password"
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="re_password">
        <el-input
          v-model="userPasswordForm.re_password"
          autocomplete="new-password"
          maxlength="20"
          placeholder="请再次输入新密码"
          show-password
          type="password"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消修改密码 -->
      <el-button :disabled="passwordSubmitting" plain @click="dialogVisible = false">取消</el-button>
      <!-- 保存新密码 -->
      <el-button :loading="passwordSubmitting" type="primary" @click="submitPassword"> 保存 </el-button>
    </template>
  </MkDialog>
</template>
