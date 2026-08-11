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
  email_host: [{ required: true, message: '请输入 SMTP Host', trigger: 'blur' }],
  email_port: [{ required: true, message: '请输入 SMTP Port', trigger: 'blur' }],
  email_host_user: [{ required: true, message: '请输入 SMTP 账户', trigger: 'blur' }],
  email_host_password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  from_email: [{ required: true, message: '请输入发件人邮箱', trigger: 'blur' }],
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
  <MkViewLayout class="system-settings-email" :loading="loading">
    <el-form
      class="max-w-200"
      ref="emailFormRef"
      :model="emailSetting"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item label="SMTP Host" prop="email_host">
        <el-input v-model="emailSetting.email_host" placeholder="请输入 SMTP Host" />
      </el-form-item>
      <el-form-item label="SMTP Port" prop="email_port">
        <el-input v-model="emailSetting.email_port" placeholder="请输入 SMTP Port" />
      </el-form-item>

      <el-form-item label="SMTP 账户" prop="email_host_user">
        <el-input v-model="emailSetting.email_host_user" placeholder="请输入 SMTP 账户" />
      </el-form-item>
      <el-form-item label="发件人邮箱" prop="from_email">
        <el-input v-model="emailSetting.from_email" type="email" placeholder="请输入发件人邮箱" />
      </el-form-item>
      <el-form-item label="密码" prop="email_host_password">
        <el-input
          v-model="emailSetting.email_host_password"
          type="password"
          show-password
          placeholder="请输入发件人密码"
        />
      </el-form-item>
      <el-form-item>
        <div class="flex flex-col">
          <p>启用 SSL<span class="text-N500">（如果 SMTP 端口是 465，通常需要启用 SSL）</span></p>
          <el-switch v-model="emailSetting.email_use_ssl" class="self-start" />
        </div>
      </el-form-item>
      <el-form-item>
        <div class="flex flex-col">
          <p>启用 TLS<span class="text-N500">（如果 SMTP 端口是 587，通常需要启用 TL）</span></p>
          <el-switch v-model="emailSetting.email_use_tls" class="self-start" />
        </div>
      </el-form-item>

      <el-button type="primary" @click="submitEmailSetting('save')">保存</el-button>
      <el-button @click="submitEmailSetting('test')">测试连接</el-button>
    </el-form>
  </MkViewLayout>
</template>
