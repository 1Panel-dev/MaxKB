<script setup lang="ts">
import { onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import AuthSettingApi from '@/api/admin/system/auth-setting'
import { LOGIN_METHOD } from '@/api/enums'
import type { AuthProviderSettingPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'SamlAuthenticationSetting' })
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
const rules = reactive<FormRules<AuthProviderSettingPayload>>({
  'config.idpMetaUrl': [{ required: true, message: '请输入 Idp MetaData Url', trigger: 'blur' }],
  'config.privateKey': [{ required: true, message: '请输入 SP Private Key', trigger: 'blur' }],
  'config.certificate': [{ required: true, message: '请输入 SP Certificate', trigger: 'blur' }],
  'config.mapping': [{ required: true, message: '请输入字段映射', trigger: 'blur' }],
  'config.spEntityId': [{ required: true, message: '请输入 SP Entity Id', trigger: 'blur' }],
  'config.spAcs': [{ required: true, message: '请输入 SP Ace', trigger: 'blur' }],
})

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
          mapping:
            typeof mapping === 'string' && mapping
              ? JSON.stringify(JSON.parse(mapping))
              : mapping || '',
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
      .then(() => MsgSuccess('保存成功'))
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
    label-position="top"
  >
    <el-form-item label="Idp MetaData Url" prop="config.idpMetaUrl"
      ><el-input v-model="form.config.idpMetaUrl" placeholder="请输入 Idp MetaData Url"
    /></el-form-item>
    <el-form-item
      ><div class="flex flex-col">
        <span>开启请求签名</span
        ><el-switch v-model="form.config.wantAssertionsSigned" class="self-start" /></div
    ></el-form-item>
    <el-form-item
      ><div class="flex flex-col">
        <span>开启断言签名</span
        ><el-switch v-model="form.config.wantAuthnRequestsSigned" class="self-start" /></div
    ></el-form-item>
    <el-form-item label="SP Private Key" prop="config.privateKey"
      ><el-input
        v-model="form.config.privateKey"
        placeholder="请输入 SP Private Key"
        type="password"
        show-password
    /></el-form-item>
    <el-form-item label="SP Certificate" prop="config.certificate"
      ><el-input
        v-model="form.config.certificate"
        placeholder="请输入 SP Certificate"
        type="password"
        show-password
    /></el-form-item>
    <el-form-item label="字段映射" prop="config.mapping"
      ><el-input v-model="form.config.mapping" placeholder="请输入字段映射"
    /></el-form-item>
    <el-form-item label="SP Entity ID" prop="config.spEntityId"
      ><el-input v-model="form.config.spEntityId" placeholder="请输入 SP Entity ID"
    /></el-form-item>
    <el-form-item label="SP ACS" prop="config.spAcs"
      ><el-input v-model="form.config.spAcs" placeholder="请输入 SP ACS"
    /></el-form-item>
    <el-form-item
      ><div class="flex flex-col">
        <span>启用 SAML2 认证</span><el-switch v-model="form.is_active" class="self-start" /></div
    ></el-form-item>
    <el-button type="primary" @click="submit">保存</el-button>
  </el-form>
</template>
