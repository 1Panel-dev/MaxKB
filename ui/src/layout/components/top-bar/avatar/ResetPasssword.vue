<template>
  <el-dialog v-model="resetPasswordDialog" title="修改密码">
    <el-form
      class="reset-password-form"
      ref="resetPasswordFormRef"
      :model="resetPasswordForm"
      :rules="rules"
    >
      <el-form-item prop="password">
        <el-input
          type="password"
          size="large"
          class="input-item"
          v-model="resetPasswordForm.password"
          placeholder="请输入密码"
        >
          <template #prepend>
            <el-button icon="Lock" />
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="re_password">
        <el-input
          type="password"
          size="large"
          class="input-item"
          v-model="resetPasswordForm.re_password"
          placeholder="请输入确认密码"
        >
          <template #prepend>
            <el-button icon="Lock" />
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-input
          size="large"
          class="input-item"
          :disabled="true"
          v-bind:modelValue="user.userInfo?.email"
          placeholder="请输入邮箱"
        >
          <template #prepend>
            <el-button icon="UserFilled" />
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="code">
        <div class="flex-between w-full">
          <el-input
            size="large"
            class="code-input"
            v-model="resetPasswordForm.code"
            placeholder="请输入验证码"
          >
            <template #prepend>
              <el-button icon="Key" />
            </template>
          </el-input>
          <el-button
            size="large"
            class="send-email-button ml-10"
            @click="sendEmail"
            :loading="loading"
            >获取验证码</el-button
          >
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="resetPassword"> 修改密码 </el-button>
      </span>
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

const rules = ref<FormRules<ResetCurrentUserPasswordRequest>>({
  code: [{ required: true, message: '请输入验证码' }],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 30,
      message: '长度在 6 到 30 个字符',
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: '请输入确认密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 30,
      message: '长度在 6 到 30 个字符',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (resetPasswordForm.value.password != resetPasswordForm.value.re_password) {
          callback(new Error('密码不一致'))
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
    MsgSuccess('发送验证码成功')
  })
}

const open = () => {
  resetPasswordForm.value = {
    code: '',
    password: '',
    re_password: ''
  }
  resetPasswordDialog.value = true
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
