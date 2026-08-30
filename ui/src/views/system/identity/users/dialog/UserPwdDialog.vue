<script setup lang="ts">
import { reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import UserManageApi from '@/api/admin/system/user-manage'
import type { SystemUser, UpdatePasswordForm } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'UserPwdDialog' })

const emit = defineEmits<{ refresh: [] }>()

const router = useRouter()
const { auth, user } = useStore()

const dialogVisible = ref(false)
const passwordSubmitting = ref(false)

const userId = ref('')
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

function open(user: SystemUser) {
  userId.value = user.id
  dialogVisible.value = true
}

async function submitPassword() {
  userPasswordFormRef.value?.validate((valid) => {
    if (!valid) return
    passwordSubmitting.value = true
    const encryptor = new JSEncrypt()
    encryptor.setPublicKey(auth.baseProfile?.rsa ?? '')
    const encryptedData = encryptor.encrypt(JSON.stringify(userPasswordForm))
    if (!encryptedData) {
      passwordSubmitting.value = false
      return
    }

    return UserManageApi.putUserPassword(userId.value, { encryptedData })
      .then(() => {
        MsgSuccess('密码修改成功')

        if (userId.value === user.userInfo?.id) {
          auth.clearToken()
          return router.push({ name: 'login' }).then(() => undefined)
        }
        emit('refresh')
        dialogVisible.value = false
      })
      .finally(() => {
        passwordSubmitting.value = false
      })
  })
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
    <el-form ref="userPasswordFormRef" :model="userPasswordForm" :rules="userPasswordRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="新密码" prop="password">
        <el-input v-model="userPasswordForm.password" autocomplete="new-password" maxlength="20" placeholder="请输入新密码" show-password type="password" />
      </el-form-item>
      <el-form-item label="确认密码" prop="re_password">
        <el-input v-model="userPasswordForm.re_password" autocomplete="new-password" maxlength="20" placeholder="请再次输入新密码" show-password type="password" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="dialogVisible = false">取消</el-button>
      <el-button :loading="passwordSubmitting" type="primary" @click="submitPassword"> 保存 </el-button>
    </template>
  </MkDialog>
</template>
