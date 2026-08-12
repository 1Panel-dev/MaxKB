<script setup lang="ts">
import AuthProviderForm, { type AuthProviderField } from './AuthProviderForm.vue'

defineOptions({ name: 'SamlAuthenticationSetting' })

const apiBaseUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api/saml2`
const fields: AuthProviderField[] = [
  { key: 'idpMetaUrl', label: 'Identity Provider 元数据地址' },
  {
    key: 'wantAssertionsSigned',
    label: '要求 Assertions 签名',
    defaultValue: true,
    required: false,
    type: 'switch',
  },
  {
    key: 'wantAuthnRequestsSigned',
    label: '对认证请求签名',
    defaultValue: true,
    required: false,
    type: 'switch',
  },
  { key: 'privateKey', label: '私钥', type: 'textarea' },
  { key: 'certificate', label: '证书', type: 'textarea' },
  { key: 'mapping', label: '字段映射', type: 'textarea' },
  { key: 'spEntityId', label: 'SP Entity ID', defaultValue: `${apiBaseUrl}/metadata` },
  { key: 'spAcs', label: 'SP ACS', defaultValue: `${apiBaseUrl}/sso` },
]
</script>

<template>
  <AuthProviderForm auth-type="SAML2" :fields="fields" />
</template>
