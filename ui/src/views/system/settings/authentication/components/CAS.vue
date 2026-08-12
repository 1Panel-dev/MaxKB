<script setup lang="ts">
import AuthProviderForm, { type AuthProviderField } from './AuthProviderForm.vue'

const callbackUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api/cas`
const fields: AuthProviderField[] = [
  { key: 'ldpUri', label: 'CAS 服务地址' },
  { key: 'validateUrl', label: '校验地址' },
  { key: 'redirectUrl', label: '回调地址', defaultValue: callbackUrl },
]
</script>

<template>
  <AuthProviderForm auth-type="CAS" :fields="fields" />
</template>
