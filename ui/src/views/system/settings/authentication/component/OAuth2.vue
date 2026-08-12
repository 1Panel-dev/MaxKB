<script setup lang="ts">
import AuthProviderForm, { type AuthProviderField } from './AuthProviderForm.vue'

const callbackUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api/oauth2`
const fields: AuthProviderField[] = [
  { key: 'authEndpoint', label: '授权端点' },
  { key: 'tokenEndpoint', label: 'Token 端点' },
  { key: 'userInfoEndpoint', label: '用户信息端点' },
  { key: 'scope', label: 'Scope' },
  { key: 'clientId', label: 'Client ID' },
  { key: 'clientSecret', label: 'Client Secret', type: 'password' },
  { key: 'fieldMapping', label: '字段映射', type: 'textarea' },
  { key: 'redirectUrl', label: '回调地址', defaultValue: callbackUrl },
]
</script>

<template>
  <AuthProviderForm auth-type="OAuth2" :fields="fields" />
</template>
