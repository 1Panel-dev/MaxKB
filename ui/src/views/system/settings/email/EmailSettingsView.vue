<script setup lang="ts">
import { onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { EmailSetting } from '@/api/types'
import EmailSettingApi from '@/api/admin/system/email-setting'
import { MsgSuccess } from '@/utils/message'

const defaultEmailSetting: EmailSetting = {
  email_host: '',
  email_host_password: '',
  email_host_user: '',
  email_port: '',
  email_use_ssl: false,
  email_use_tls: false,
  from_email: '',
}

const emailFormRef = useTemplateRef<FormInstance>('emailFormRef')
const emailSetting = reactive<EmailSetting>({ ...defaultEmailSetting })
const loading = ref(false)
const rules: FormRules<EmailSetting> = {
  email_host: [{ required: true, message: '请输入 SMTP 主机地址', trigger: 'blur' }],
  email_port: [{ required: true, message: '请输入 SMTP 端口', trigger: 'blur' }],
  email_host_user: [{ required: true, message: '请输入 SMTP 用户名', trigger: 'blur' }],
  email_host_password: [{ required: true, message: '请输入 SMTP 密码', trigger: 'blur' }],
  from_email: [
    { required: true, message: '请输入发件人邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
}

/* 邮箱设置加载与提交 */
function loadEmailSetting() {
  loading.value = true
  return EmailSettingApi.getEmailSetting()
    .then((setting) => Object.assign(emailSetting, defaultEmailSetting, setting))
    .finally(() => {
      loading.value = false
    })
}

function submitEmailSetting(action: 'save' | 'test') {
  emailFormRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    const request =
      action === 'test'
        ? EmailSettingApi.postEmailSettingTest(emailSetting)
        : EmailSettingApi.putEmailSetting(emailSetting)

    request
      .then(() => MsgSuccess(action === 'test' ? '测试成功' : '保存成功'))
      .finally(() => {
        loading.value = false
      })
  })
}

onMounted(loadEmailSetting)
</script>

<template>
  <MkViewLayout class="system-settings-email" v-loading="loading">
    <el-form
      ref="emailFormRef"
      class="max-w-3xl"
      :model="emailSetting"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
    >
      <div class="grid grid-cols-2 gap-x-4">
        <el-form-item label="SMTP 主机" prop="email_host">
          <el-input v-model="emailSetting.email_host" placeholder="例如 smtp.example.com" />
        </el-form-item>
        <el-form-item label="SMTP 端口" prop="email_port">
          <el-input v-model="emailSetting.email_port" placeholder="例如 465" />
        </el-form-item>
      </div>
      <el-form-item label="SMTP 用户名" prop="email_host_user">
        <el-input v-model="emailSetting.email_host_user" placeholder="请输入 SMTP 用户名" />
      </el-form-item>
      <el-form-item label="发件人邮箱" prop="from_email">
        <el-input v-model="emailSetting.from_email" type="email" placeholder="请输入发件人邮箱" />
      </el-form-item>
      <el-form-item label="SMTP 密码" prop="email_host_password">
        <el-input
          v-model="emailSetting.email_host_password"
          type="password"
          show-password
          placeholder="请输入 SMTP 密码或授权码"
        />
      </el-form-item>
      <div class="mb-4 flex gap-6">
        <el-checkbox v-model="emailSetting.email_use_ssl">启用 SSL</el-checkbox>
        <el-checkbox v-model="emailSetting.email_use_tls">启用 TLS</el-checkbox>
      </div>
      <div class="flex gap-3">
        <el-button type="primary" @click="submitEmailSetting('save')">保存</el-button>
        <el-button @click="submitEmailSetting('test')">测试连接</el-button>
      </div>
    </el-form>
  </MkViewLayout>
</template>
