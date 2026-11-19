<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AuthProviderSettingPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import AuthSettingApi from '@/api/admin/system/settings/auth-setting'
import { MsgSuccess } from '@/utils/message'
import perm from '@/permission'

defineOptions({ name: 'SamlAuthenticationSetting' })
const { t } = useI18n({ useScope: 'global' })
const samlApiBaseUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api/saml2`
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSettingPayload>({
  auth_type: LOGIN_METHOD.SAML2,
  config: {
    idpMetaUrl: '',
    wantAssertionsSigned: true,
    wantAuthnRequestsSigned: true,
    privateKey: '',
    certificate: '',
    mapping: '',
    spEntityId: `${samlApiBaseUrl}/metadata`,
    spAcs: `${samlApiBaseUrl}/sso`,
  },
  is_active: false,
})
const rules = computed<FormRules<AuthProviderSettingPayload>>(() => ({
  'config.idpMetaUrl': [
    { whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'Idp MetaData Url' }), trigger: 'blur' },
  ],
  'config.privateKey': [
    { whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'SP Private Key' }), trigger: 'blur' },
  ],
  'config.certificate': [
    { whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'SP Certificate' }), trigger: 'blur' },
  ],
  'config.mapping': [{ whitespace: true, required: true, message: t('auth.fields.fieldMapping.requiredMessage'), trigger: 'blur' }],
  'config.spEntityId': [
    { whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'SP Entity ID' }), trigger: 'blur' },
  ],
  'config.spAcs': [{ whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'SP ACS' }), trigger: 'blur' }],
}))

function loadSetting() {
  loading.value = true

  return AuthSettingApi.getAuthSetting(form.auth_type)
    .then((setting) => {
      const settingConfig = setting.config ?? {}
      const mapping = settingConfig.mapping

      Object.assign(form, setting, {
        config: {
          ...form.config,
          ...settingConfig,
          mapping: typeof mapping === 'string' && mapping ? JSON.stringify(JSON.parse(mapping)) : mapping || '',
          spEntityId: settingConfig.spEntityId || `${samlApiBaseUrl}/metadata`,
          spAcs: settingConfig.spAcs || `${samlApiBaseUrl}/sso`,
        },
      })
    })
    .finally(() => {
      loading.value = false
    })
}
function submit() {
  authFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    AuthSettingApi.putAuthSetting(form.auth_type, form)
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
    <el-form-item label="Idp MetaData Url" prop="config.idpMetaUrl">
      <el-input v-model="form.config.idpMetaUrl" :placeholder="t('common.placeholders.inputField', { label: 'Idp MetaData Url' })" />
    </el-form-item>
    <el-form-item>
      <div class="flex-column">
        <span>{{ t('auth.saml2.requestSigning') }}</span>
        <el-switch v-model="form.config.wantAssertionsSigned" class="self-start" />
      </div>
    </el-form-item>
    <el-form-item>
      <div class="flex-column">
        <span>{{ t('auth.saml2.assertionSigning') }}</span>
        <el-switch v-model="form.config.wantAuthnRequestsSigned" class="self-start" />
      </div>
    </el-form-item>
    <el-form-item label="SP Private Key" prop="config.privateKey">
      <el-input
        v-model="form.config.privateKey"
        :placeholder="t('common.placeholders.inputField', { label: 'SP Private Key' })"
        type="password"
        autocomplete="new-password"
        show-password
      />
    </el-form-item>
    <el-form-item label="SP Certificate" prop="config.certificate">
      <el-input
        v-model="form.config.certificate"
        :placeholder="t('common.placeholders.inputField', { label: 'SP Certificate' })"
        type="password"
        autocomplete="new-password"
        show-password
      />
    </el-form-item>
    <el-form-item :label="t('auth.fields.fieldMapping.label')" prop="config.mapping">
      <el-input v-model="form.config.mapping" :placeholder="t('auth.fields.fieldMapping.placeholder')" />
    </el-form-item>
    <el-form-item label="SP Entity ID" prop="config.spEntityId">
      <el-input v-model="form.config.spEntityId" :placeholder="t('common.placeholders.inputField', { label: 'SP Entity ID' })" />
    </el-form-item>
    <el-form-item label="SP ACS" prop="config.spAcs">
      <el-input v-model="form.config.spAcs" :placeholder="t('common.placeholders.inputField', { label: 'SP ACS' })" />
    </el-form-item>
    <el-form-item>
      <div class="flex-column">
        <span>{{ t('auth.enableAuthentication', { provider: LOGIN_METHOD.SAML2 }) }}</span>
        <el-switch v-model="form.is_active" class="self-start" />
      </div>
    </el-form-item>
    <!-- 保存 -->
    <el-button v-if="perm.system.loginAuth.edit()" type="primary" @click="submit">{{ t('common.actions.save') }}</el-button>
  </el-form>
</template>
