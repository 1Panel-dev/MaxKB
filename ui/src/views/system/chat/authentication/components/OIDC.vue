<script setup lang="ts">
import { onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserAuthApi from '@/api/admin/system/chat-user/chat-user-auth'
import { LOGIN_METHOD } from '@/api/enums'
import type { AuthProviderSettingPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'OidcAuthenticationSetting' })
const defaultFieldMapping = '{"username":"preferred_username","email":"email"}'
const defaultRedirectUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api/oidc`

const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSettingPayload>({
  auth_type: LOGIN_METHOD.OIDC,
  config: {
    authEndpoint: '',
    tokenEndpoint: '',
    userInfoEndpoint: '',
    scope: '',
    state: '',
    clientId: '',
    clientSecret: '',
    fieldMapping: defaultFieldMapping,
    redirectUrl: defaultRedirectUrl,
  },
  is_active: false,
})
const rules = reactive<FormRules<AuthProviderSettingPayload>>({
  'config.authEndpoint': [{ required: true, message: '请输入授权端地址', trigger: 'blur' }],
  'config.tokenEndpoint': [{ required: true, message: '请输入 Token 端地址', trigger: 'blur' }],
  'config.userInfoEndpoint': [{ required: true, message: '请输入用户信息端地址', trigger: 'blur' }],
  'config.scope': [{ required: true, message: '请输入 Scope', trigger: 'blur' }],
  'config.clientId': [{ required: true, message: '请输入客户端 ID', trigger: 'blur' }],
  'config.clientSecret': [{ required: true, message: '请输入客户端密钥', trigger: 'blur' }],
  'config.fieldMapping': [{ required: true, message: '请输入字段映射', trigger: 'blur' }],
  'config.redirectUrl': [{ required: true, message: '请输入回调地址', trigger: 'blur' }],
})

function loadSetting() {
  loading.value = true

  return ChatUserAuthApi.getAuthSetting(form.auth_type)
    .then((setting) => {
      const settingConfig = setting.config ?? {}
      Object.assign(form, setting, {
        config: { ...form.config, ...settingConfig, fieldMapping: settingConfig.fieldMapping || defaultFieldMapping, redirectUrl: settingConfig.redirectUrl || defaultRedirectUrl },
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
    ChatUserAuthApi.putAuthSetting(form.auth_type, form)
      .then(() => MsgSuccess('保存成功'))
      .finally(() => (loading.value = false))
  })
}
onMounted(() => loadSetting())
</script>

<template>
  <el-form ref="authFormRef" v-loading="loading" class="max-w-200" :model="form" :rules="rules" label-position="top">
    <el-form-item label="授权端地址" prop="config.authEndpoint"><el-input v-model="form.config.authEndpoint" placeholder="请输入授权端地址" /></el-form-item>
    <el-form-item label="Token 端地址" prop="config.tokenEndpoint"><el-input v-model="form.config.tokenEndpoint" placeholder="请输入 Token 端地址" /></el-form-item>
    <el-form-item label="用户信息端地址" prop="config.userInfoEndpoint"><el-input v-model="form.config.userInfoEndpoint" placeholder="请输入用户信息端地址" /></el-form-item>
    <el-form-item label="Scope" prop="config.scope"><el-input v-model="form.config.scope" placeholder="openid+profile+email" /></el-form-item>
    <el-form-item label="State"><el-input v-model="form.config.state" placeholder="请输入" /></el-form-item>
    <el-form-item label="客户端 ID" prop="config.clientId"><el-input v-model="form.config.clientId" placeholder="请输入客户端 ID" /></el-form-item>
    <el-form-item label="客户端密钥" prop="config.clientSecret"
      ><el-input v-model="form.config.clientSecret" type="password" show-password placeholder="请输入客户端密钥"
    /></el-form-item>
    <el-form-item label="字段映射" prop="config.fieldMapping"><el-input v-model="form.config.fieldMapping" placeholder="请输入字段映射" /></el-form-item>
    <el-form-item label="回调地址" prop="config.redirectUrl"><el-input v-model="form.config.redirectUrl" placeholder="请输入回调地址" /></el-form-item>
    <el-form-item
      ><div class="flex flex-col"><span>启用 OIDC 认证</span><el-switch v-model="form.is_active" class="self-start" /></div
    ></el-form-item>
    <el-button type="primary" @click="submit">保存</el-button>
  </el-form>
</template>
