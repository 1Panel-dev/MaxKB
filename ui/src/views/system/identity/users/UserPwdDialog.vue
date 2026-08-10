<script setup lang="ts">
import { reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import type { FormInstance, FormRules } from 'element-plus'
import UserManageApi from '@/api/admin/system/user-manage'
import { useStore } from '@/stores'
import type { SystemUser } from '@/api/types'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'UserPwdDialog' })

interface UserPasswordForm {
  password: string
  re_password: string
}

const emit = defineEmits<{
  refresh: [resetQuery: boolean]
}>()

const { auth } = useStore()
const dialogVisible = ref(false)
const passwordSubmitting = ref(false)
const userId = ref('')
const userPasswordFormRef = ref<FormInstance>()
const userPasswordForm = reactive<UserPasswordForm>({
  password: '',
  re_password: '',
})

function validateConfirmPassword(_rule: unknown, value: string, callback: (error?: Error) => void) {
  if (!value) {
    callback(new Error('请输入确认密码'))
  } else if (value !== userPasswordForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordPattern =
  /^(?=.*[a-z])(?=.*[-_!@#$%^&*`~.()+=])(?:(?=.*[A-Z])|(?=.*\d))[a-zA-Z0-9-_!@#$%^&*`~.()+=]{6,20}$/
const userPasswordRules = reactive<FormRules<UserPasswordForm>>({
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    {
      pattern: passwordPattern,
      message: '密码需为6-20位，并包含小写字母、特殊字符及大写字母或数字',
      trigger: 'blur',
    },
  ],
  re_password: [{ validator: validateConfirmPassword, trigger: 'blur' }],
})

function open(user: Pick<SystemUser, 'id'>) {
  userId.value = user.id
  dialogVisible.value = true
}

async function submitPassword() {
  const valid = await userPasswordFormRef.value?.validate().catch(() => false)
  if (!valid) return

  const encryptor = new JSEncrypt()
  encryptor.setPublicKey(auth.baseProfile?.rsa ?? '')
  const encryptedData = encryptor.encrypt(JSON.stringify(userPasswordForm))
  if (!encryptedData) {
    MsgError('密码加密失败')
    return
  }

  passwordSubmitting.value = true
  return UserManageApi.putUserPassword(userId.value, { encryptedData })
    .then(() => {
      MsgSuccess('密码修改成功')
      emit('refresh', false)
      close()
    })
    .finally(() => {
      passwordSubmitting.value = false
    })
}
function close() {
  dialogVisible.value = false
  resetData()
}

function resetData() {
  Object.assign(userPasswordForm, { password: '', re_password: '' })
  passwordSubmitting.value = false
  userId.value = ''
  userPasswordFormRef.value?.clearValidate()
}
defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="修改用户密码" @closed="resetData">
    <el-form
      ref="userPasswordFormRef"
      :model="userPasswordForm"
      :rules="userPasswordRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitPassword"
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
      <el-button @click="close">取消</el-button>
      <el-button :loading="passwordSubmitting" type="primary" @click="submitPassword">
        保存
      </el-button>
    </template>
  </MkDialog>
</template>
