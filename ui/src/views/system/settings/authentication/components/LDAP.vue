<script setup lang="ts">
import AuthProviderForm, { type AuthProviderField } from './AuthProviderForm.vue'

const fields: AuthProviderField[] = [
  { key: 'ldap_server', label: '服务器地址', placeholder: '例如：ldap://127.0.0.1:389' },
  { key: 'base_dn', label: 'Bind DN' },
  { key: 'password', label: '密码', type: 'password' },
  { key: 'ou', label: '用户目录（OU）' },
  { key: 'ldap_filter', label: '用户过滤器' },
  {
    key: 'ldap_mapping',
    label: '字段映射',
    placeholder: '{"name":"name","email":"mail","username":"cn"}',
    type: 'textarea',
  },
]
</script>

<template>
  <AuthProviderForm auth-type="LDAP" :fields="fields" testable />
</template>
