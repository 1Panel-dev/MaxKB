<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AuthProviderSettingPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import ChatUserAuthApi from '@/api/admin/system/chat-management/chat-user-auth'
import { CHAT_API_BASE_PATH } from '@/api/constants.ts'
import { MsgSuccess } from '@/utils/message'
import perm from '@/permission'

defineOptions({ name: 'OidcAuthenticationSetting' })
const { t } = useI18n({ useScope: 'global' })

const defaultRedirectUrl = `${window.location.origin}${CHAT_API_BASE_PATH}/auth/oauth2`

const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSettingPayload>({
  auth_type: LOGIN_METHOD.OAUTH2,
  config: {
    authEndpoint: '',
    tokenEndpoint: '',
    userInfoEndpoint: '',
    scope: '',
    clientId: '',
    clientSecret: '',
    redirectUrl: defaultRedirectUrl,
    fieldMapping: '',
  },
  is_active: false,
})
const rules = computed<FormRules<AuthProviderSettingPayload>>(() => ({
  'config.authEndpoint': [{ whitespace: true, required: true, message: t('auth.fields.authEndpoint.requiredMessage'), trigger: 'blur' }],
  'config.tokenEndpoint': [{ whitespace: true, required: true, message: t('auth.fields.tokenEndpoint.requiredMessage'), trigger: 'blur' }],
  'config.userInfoEndpoint': [{ whitespace: true, required: true, message: t('auth.fields.userInfoEndpoint.requiredMessage'), trigger: 'blur' }],
  'config.scope': [{ whitespace: true, required: true, message: t('auth.oauth2.scope.requiredMessage'), trigger: 'blur' }],
  'config.clientId': [{ whitespace: true, required: true, message: t('auth.fields.clientId.requiredMessage'), trigger: 'blur' }],
  'config.clientSecret': [{ whitespace: true, required: true, message: t('auth.fields.clientSecret.requiredMessage'), trigger: 'blur' }],
  'config.fieldMapping': [{ whitespace: true, required: true, message: t('auth.fields.fieldMapping.requiredMessage'), trigger: 'blur' }],
  'config.redirectUrl': [{ whitespace: true, required: true, message: t('auth.fields.callbackUrl.requiredMessage'), trigger: 'blur' }],
}))

function loadSetting() {
  loading.value = true

  return ChatUserAuthApi.getAuthSetting(form.auth_type)
    .then((setting) => {
      const settingConfig = setting.config ?? {}
      Object.assign(form, setting, { config: { ...form.config, ...settingConfig, redirectUrl: settingConfig.redirectUrl || defaultRedirectUrl } })
    })
    .finally(() => {
      loading.value = false
    })
}
function submit() {
  authFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    ChatUserAuthApi.putAuthSetting(form.auth_type, form)
      .then(() => MsgSuccess(t('common.messages.saveSuccess')))
      .finally(() => (loading.value = false))
  })
}
onMounted(() => loadSetting())
</script>

<template>
  <el-form
    ref="authFormRef"
    v-loading="loading"
    class="max-w-200"
    :model="form"
    :rules="rules"
    :validate-on-rule-change="false"
    label-position="top"
    require-asterisk-position="right"
    @submit.prevent
  >
    <el-form-item :label="t('auth.fields.authEndpoint.label')" prop="config.authEndpoint">
      <el-input v-model="form.config.authEndpoint" :placeholder="t('auth.fields.authEndpoint.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.fields.tokenEndpoint.label')" prop="config.tokenEndpoint">
      <el-input v-model="form.config.tokenEndpoint" :placeholder="t('auth.fields.tokenEndpoint.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.fields.userInfoEndpoint.label')" prop="config.userInfoEndpoint">
      <el-input v-model="form.config.userInfoEndpoint" :placeholder="t('auth.fields.userInfoEndpoint.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.oauth2.scope.label')" prop="config.scope">
      <el-input v-model="form.config.scope" :placeholder="t('auth.oauth2.scope.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.fields.clientId.label')" prop="config.clientId">
      <el-input v-model="form.config.clientId" :placeholder="t('auth.fields.clientId.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.fields.clientSecret.label')" prop="config.clientSecret">
      <el-input
        v-model="form.config.clientSecret"
        type="password"
        autocomplete="new-password"
        show-password
        :placeholder="t('auth.fields.clientSecret.placeholder')"
      />
    </el-form-item>
    <el-form-item :label="t('auth.fields.fieldMapping.label')" prop="config.fieldMapping">
      <el-input v-model="form.config.fieldMapping" :placeholder="t('auth.fields.fieldMapping.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.fields.callbackUrl.label')" prop="config.redirectUrl">
      <el-input v-model="form.config.redirectUrl" :placeholder="t('auth.fields.callbackUrl.placeholder')" />
    </el-form-item>
    <el-form-item>
      <div class="flex-column">
        <span>{{ t('auth.enableAuthentication', { provider: LOGIN_METHOD.OAUTH2 }) }}</span>
        <el-switch v-model="form.is_active" class="self-start" />
      </div>
    </el-form-item>
    <!-- 保存 -->
    <el-button v-if="perm.system.chatAuth.edit()" type="primary" @click="submit">{{ t('common.actions.save') }}</el-button>
  </el-form>
</template>
