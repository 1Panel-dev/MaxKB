<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AuthProviderSettingPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import AuthSettingApi from '@/api/admin/system/settings/auth-setting'
import { MsgSuccess } from '@/utils/message'
import perm from '@/permission'

defineOptions({ name: 'CasAuthenticationSetting' })
const { t } = useI18n({ useScope: 'global' })

const defaultRedirectUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api/cas`
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSettingPayload>({
  auth_type: LOGIN_METHOD.CAS,
  config: { ldpUri: '', validateUrl: '', redirectUrl: defaultRedirectUrl },
  is_active: false,
})
const rules = computed<FormRules<AuthProviderSettingPayload>>(() => ({
  'config.ldpUri': [{ whitespace: true, required: true, message: t('common.validation.inputFieldRequired', { label: 'ldpUri' }), trigger: 'blur' }],
  'config.validateUrl': [{ whitespace: true, required: true, message: t('auth.cas.validateUrl.requiredMessage'), trigger: 'blur' }],
  'config.redirectUrl': [{ whitespace: true, required: true, message: t('auth.fields.callbackUrl.requiredMessage'), trigger: 'blur' }],
}))

function loadSetting() {
  loading.value = true

  return AuthSettingApi.getAuthSetting(form.auth_type)
    .then((setting) => {
      const settingConfig = setting.config ?? {}
      const ldpUri = settingConfig.ldpUri ?? ''

      Object.assign(form, setting, {
        config: {
          ...form.config,
          ...settingConfig,
          validateUrl: settingConfig.validateUrl || ldpUri,
          redirectUrl: settingConfig.redirectUrl || defaultRedirectUrl,
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
    <el-form-item label="ldpUri" prop="config.ldpUri">
      <el-input v-model="form.config.ldpUri" :placeholder="t('common.placeholders.inputField', { label: 'ldpUri' })" />
    </el-form-item>
    <el-form-item :label="t('auth.cas.validateUrl.label')" prop="config.validateUrl">
      <el-input v-model="form.config.validateUrl" :placeholder="t('auth.cas.validateUrl.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.fields.callbackUrl.label')" prop="config.redirectUrl">
      <el-input v-model="form.config.redirectUrl" :placeholder="t('auth.fields.callbackUrl.placeholder')" />
    </el-form-item>
    <el-form-item>
      <div class="flex-column">
        <span>{{ t('auth.enableAuthentication', { provider: LOGIN_METHOD.CAS }) }}</span>
        <el-switch v-model="form.is_active" class="self-start" />
      </div>
    </el-form-item>
    <!-- 保存 -->
    <el-button v-if="perm.system.loginAuth.edit()" type="primary" @click="submit">{{ t('common.actions.save') }}</el-button>
  </el-form>
</template>
