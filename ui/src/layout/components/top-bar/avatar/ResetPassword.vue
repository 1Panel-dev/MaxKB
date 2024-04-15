<template>
  <el-dialog v-model="resetPasswordDialog" title="修改密码">
    <el-form
      class="reset-password-form mb-24"
      ref="resetPasswordFormRef"
      :model="resetPasswordForm"
      :rules="rules"
    >
      <p class="mb-8 lighter">新密码</p>
      <el-form-item prop="password" style="margin-bottom: 8px">
        <el-input
          type="password"
          class="input-item"
          v-model="resetPasswordForm.password"
          placeholder="请输入密码"
          show-password
        >
        </el-input>
      </el-form-item>
      <el-form-item prop="re_password">
        <el-input
          type="password"
          class="input-item"
          v-model="resetPasswordForm.re_password"
          placeholder="请输入确认密码"
          show-password
        >
        </el-input>
      </el-form-item>
      <p class="mb-8 lighter">使用邮箱</p>
      <el-form-item style="margin-bottom: 8px">
        <el-input
          class="input-item"
          :disabled="true"
          v-bind:modelValue="user.userInfo?.email"
          placeholder="请输入邮箱"
        >
        </el-input>
      </el-form-item>
      <el-form-item prop="code">
        <div class="flex-between w-full">
          <el-input class="code-input" v-model="resetPasswordForm.code" placeholder="请输入验证码">
          </el-input>
          <el-button
            :disabled="isDisabled"
            class="send-email-button ml-8"
            @click="sendEmail"
            :loading="loading"
          >
            {{ isDisabled ? `重新发送（${time}s）` : '获取验证码' }}</el-button
          >
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="resetPasswordDialog = false"> 取消 </el-button>
        <el-button type="primary" @click="resetPassword"> 保存 </el-button>
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
  code: [{ required: true, message: '请输入验证码' }],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: '长度在 6 到 20 个字符',
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
      max: 20,
      message: '长度在 6 到 20 个字符',
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
