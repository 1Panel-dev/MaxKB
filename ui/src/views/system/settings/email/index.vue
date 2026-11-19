<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { EmailSettingPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import EmailSettingApi from '@/api/admin/system/settings/email-setting'
import { MsgSuccess } from '@/utils/message'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })
const defaultEmailSetting: EmailSettingPayload = {
  email_host: '',
  email_host_password: '',
  email_host_user: '',
  email_port: '',
  email_use_ssl: false,
  email_use_tls: false,
  from_email: '',
}

const emailFormRef = useTemplateRef<FormInstance>('emailFormRef')
const emailSetting = reactive<EmailSettingPayload>({ ...defaultEmailSetting })
const loading = ref(false)
const rules = computed<FormRules<EmailSettingPayload>>(() => ({
  email_host: [{ whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'SMTP Host' }), trigger: 'blur' }],
  email_port: [{ whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'SMTP Port' }), trigger: 'blur' }],
  email_host_user: [{ whitespace: true, required: true, message: t('email.account.requiredMessage'), trigger: 'blur' }],
  email_host_password: [{ required: true, message: t('auth.fields.password.requiredMessage'), trigger: 'blur' }],
  from_email: [{ whitespace: true, required: true, message: t('email.senderEmail.requiredMessage'), trigger: 'blur' }],
}))

/* 邮箱设置加载与提交 */
function loadEmailSetting() {
  loading.value = true
  return EmailSettingApi.getEmailSetting()
    .then((setting) => {
      // 兼容接口返回数字端口，统一使用字符串进行回显、校验和提交。
      Object.assign(emailSetting, defaultEmailSetting, setting, {
        email_port: String(setting.email_port ?? ''),
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function submitEmailSetting(action: 'save' | 'test') {
  emailFormRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    const request = action === 'test' ? EmailSettingApi.postEmailSettingTest(emailSetting) : EmailSettingApi.putEmailSetting(emailSetting)

    request
      .then(() => MsgSuccess(action === 'test' ? t('common.messages.testSuccess') : t('common.messages.saveSuccess')))
      .finally(() => {
        loading.value = false
      })
  })
}

onMounted(() => loadEmailSetting())
</script>

<template>
  <MkViewLayout :title="t('email.title')" class="system-settings-email" :loading="loading">
    <el-form
      class="max-w-200"
      ref="emailFormRef"
      :model="emailSetting"
      :rules="rules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="SMTP Host" prop="email_host">
        <el-input v-model="emailSetting.email_host" :placeholder="t('common.placeholders.inputField', { label: 'SMTP Host' })" />
      </el-form-item>
      <el-form-item label="SMTP Port" prop="email_port">
        <el-input v-model="emailSetting.email_port" :placeholder="t('common.placeholders.inputField', { label: 'SMTP Port' })" />
      </el-form-item>

      <el-form-item :label="t('email.account.label')" prop="email_host_user">
        <el-input v-model="emailSetting.email_host_user" :placeholder="t('email.account.placeholder')" />
      </el-form-item>
      <el-form-item :label="t('email.senderEmail.label')" prop="from_email">
        <el-input v-model="emailSetting.from_email" type="email" :placeholder="t('email.senderEmail.placeholder')" />
      </el-form-item>
      <el-form-item :label="t('auth.fields.password.label')" prop="email_host_password">
        <el-input
          v-model="emailSetting.email_host_password"
          type="password"
          autocomplete="new-password"
          show-password
          :placeholder="t('email.password.placeholder')"
        />
      </el-form-item>
      <el-form-item>
        <div class="flex-column">
          <p>
            {{ t('email.ssl.label') }}
            <span class="text-N500">（{{ t('email.ssl.description') }}）</span>
          </p>
          <el-switch v-model="emailSetting.email_use_ssl" class="self-start" />
        </div>
      </el-form-item>
      <el-form-item>
        <div class="flex-column">
          <p>
            {{ t('email.tls.label') }}
            <span class="text-N500">（{{ t('email.tls.description') }}）</span>
          </p>
          <el-switch v-model="emailSetting.email_use_tls" class="self-start" />
        </div>
      </el-form-item>

      <!-- 保存 -->
      <el-button v-if="perm.system.email.edit()" type="primary" @click="submitEmailSetting('save')">{{ t('common.actions.save') }}</el-button>
      <!-- 测试连接 -->
      <el-button plain @click="submitEmailSetting('test')">{{ t('common.actions.testConnection') }}</el-button>
    </el-form>
  </MkViewLayout>
</template>
