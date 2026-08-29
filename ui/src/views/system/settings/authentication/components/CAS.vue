<script setup lang="ts">
import { onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import AuthSettingApi from '@/api/admin/system/settings/auth-setting'
import { LOGIN_METHOD } from '@/api/enums'
import type { AuthProviderSettingPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CasAuthenticationSetting' })

const defaultRedirectUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api/cas`
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSettingPayload>({
  auth_type: LOGIN_METHOD.CAS,
  config: { ldpUri: '', validateUrl: '', redirectUrl: defaultRedirectUrl },
  is_active: false,
})
const rules = reactive<FormRules<AuthProviderSettingPayload>>({
  'config.ldpUri': [{ required: true, message: '请输入 ldpUri', trigger: 'blur' }],
  'config.validateUrl': [{ required: true, message: '请输入验证地址', trigger: 'blur' }],
  'config.redirectUrl': [{ required: true, message: '请输入回调地址', trigger: 'blur' }],
})

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
      .then(() => MsgSuccess('保存成功'))
      .finally(() => (loading.value = false))
  })
}

onMounted(() => loadSetting)
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
    <el-form-item label="ldpUri" prop="config.ldpUri"
      ><el-input v-model="form.config.ldpUri" placeholder="请输入 ldpUri"
    /></el-form-item>
    <el-form-item label="验证地址" prop="config.validateUrl"
      ><el-input v-model="form.config.validateUrl" placeholder="请输入验证地址"
    /></el-form-item>
    <el-form-item label="回调地址" prop="config.redirectUrl"
      ><el-input v-model="form.config.redirectUrl" placeholder="请输入回调地址"
    /></el-form-item>
    <el-form-item
      ><div class="flex flex-col">
        <span>启用 CAS 认证</span>
        <el-switch v-model="form.is_active" class="self-start" />
      </div>
    </el-form-item>
    <el-button type="primary" @click="submit">保存</el-button>
  </el-form>
</template>
