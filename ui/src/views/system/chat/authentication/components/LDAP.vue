<script setup lang="ts">
import { onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserAuthApi from '@/api/admin/system/chat-user/chat-user-auth'
import { LOGIN_METHOD } from '@/api/enums'
import type { AuthProviderSettingPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'LdapAuthenticationSetting' })
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSettingPayload>({
  auth_type: LOGIN_METHOD.LDAP,
  config: { ldap_server: '', base_dn: '', password: '', ou: '', ldap_filter: '', ldap_mapping: '' },
  is_active: false,
})
const rules = reactive<FormRules<AuthProviderSettingPayload>>({
  'config.ldap_server': [{ required: true, message: '请输入服务器地址', trigger: 'blur' }],
  'config.base_dn': [{ required: true, message: '请输入Bind DN', trigger: 'blur' }],
  'config.password': [{ required: true, message: '请输入密码', trigger: 'blur' }],
  'config.ou': [{ required: true, message: '请输入用户目录（OU）', trigger: 'blur' }],
  'config.ldap_filter': [{ required: true, message: '请输入用户过滤器', trigger: 'blur' }],
  'config.ldap_mapping': [{ required: true, message: '请输入字段映射', trigger: 'blur' }],
})

function loadSetting() {
  loading.value = true
  return ChatUserAuthApi.getAuthSetting(form.auth_type)
    .then((setting) => {
      const ldapMapping = setting.config?.ldap_mapping
      Object.assign(form, setting, {
        config: {
          ...form.config,
          ...setting.config,
          ldap_mapping:
            typeof ldapMapping === 'string' && ldapMapping
              ? JSON.stringify(JSON.parse(ldapMapping))
              : ldapMapping,
        },
      })
    })
    .finally(() => (loading.value = false))
}
function submit(action: 'save' | 'test') {
  authFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    const request =
      action === 'test'
        ? ChatUserAuthApi.postAuthSettingConnection(form)
        : ChatUserAuthApi.putAuthSetting(form.auth_type, form)
    request
      .then(() => MsgSuccess(action === 'test' ? '连接成功' : '保存成功'))
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
    <el-form-item label="LDAP 地址" prop="config.ldap_server"
      ><el-input v-model="form.config.ldap_server" placeholder="请输入LDAP 地址"
    /></el-form-item>
    <el-form-item label="绑定 DN" prop="config.base_dn"
      ><el-input v-model="form.config.base_dn" placeholder="请输入绑定 DN"
    /></el-form-item>
    <el-form-item label="密码" prop="config.password">
      <el-input
        v-model="form.config.password"
        type="password"
        show-password
        placeholder="请输入密码"
      />
    </el-form-item>
    <el-form-item label="用户 OU" prop="config.ou">
      <el-input v-model="form.config.ou" placeholder="请输入用户 OU" />
    </el-form-item>
    <el-form-item label="用户过滤器" prop="config.ldap_filter"
      ><el-input v-model="form.config.ldap_filter" placeholder="请输入用户过滤器"
    /></el-form-item>
    <el-form-item label="LDAP 属性映射" prop="config.ldap_mapping"
      ><el-input
        v-model="form.config.ldap_mapping"
        type="textarea"
        :rows="4"
        placeholder="请输入 LDAP 属性映射"
    /></el-form-item>
    <el-form-item>
      <div class="flex flex-col">
        <span>启用 LDAP 认证</span>
        <el-switch v-model="form.is_active" class="self-start" />
      </div>
    </el-form-item>
    <div>
      <el-button type="primary" @click="submit('save')">保存</el-button>
      <el-button plain @click="submit('test')">测试连接</el-button>
    </div>
  </el-form>
</template>
