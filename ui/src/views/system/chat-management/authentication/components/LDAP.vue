<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AuthProviderSettingPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import ChatUserAuthApi from '@/api/admin/system/chat-management/chat-user-auth'
import { MsgSuccess } from '@/utils/message'
import perm from '@/permission'

defineOptions({ name: 'LdapAuthenticationSetting' })
const { t } = useI18n({ useScope: 'global' })
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSettingPayload>({
  auth_type: LOGIN_METHOD.LDAP,
  config: { ldap_server: '', base_dn: '', password: '', ou: '', ldap_filter: '', ldap_mapping: '' },
  is_active: false,
})
const rules = computed<FormRules<AuthProviderSettingPayload>>(() => ({
  'config.ldap_server': [{ whitespace: true, required: true, message: t('auth.ldap.server.requiredMessage'), trigger: 'blur' }],
  'config.base_dn': [{ whitespace: true, required: true, message: t('auth.ldap.bindDn.requiredMessage'), trigger: 'blur' }],
  'config.password': [{ required: true, message: t('auth.fields.password.requiredMessage'), trigger: 'blur' }],
  'config.ou': [{ whitespace: true, required: true, message: t('auth.ldap.userOu.requiredMessage'), trigger: 'blur' }],
  'config.ldap_filter': [{ whitespace: true, required: true, message: t('auth.ldap.userFilter.requiredMessage'), trigger: 'blur' }],
  'config.ldap_mapping': [{ whitespace: true, required: true, message: t('auth.ldap.attributeMapping.requiredMessage'), trigger: 'blur' }],
}))

function loadSetting() {
  loading.value = true
  return ChatUserAuthApi.getAuthSetting(form.auth_type)
    .then((setting) => {
      const ldapMapping = setting.config?.ldap_mapping
      Object.assign(form, setting, {
        config: {
          ...form.config,
          ...setting.config,
          ldap_mapping: typeof ldapMapping === 'string' && ldapMapping ? JSON.stringify(JSON.parse(ldapMapping)) : ldapMapping,
        },
      })
    })
    .finally(() => (loading.value = false))
}
function submit(action: 'save' | 'test') {
  authFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    const request = action === 'test' ? ChatUserAuthApi.postAuthSettingConnection(form) : ChatUserAuthApi.putAuthSetting(form.auth_type, form)
    request
      .then(() => MsgSuccess(action === 'test' ? t('common.messages.connectionSuccess') : t('common.messages.saveSuccess')))
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
    <el-form-item :label="t('auth.ldap.server.label')" prop="config.ldap_server">
      <el-input v-model="form.config.ldap_server" :placeholder="t('auth.ldap.server.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.ldap.bindDn.label')" prop="config.base_dn">
      <el-input v-model="form.config.base_dn" :placeholder="t('auth.ldap.bindDn.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.fields.password.label')" prop="config.password">
      <el-input
        v-model="form.config.password"
        type="password"
        autocomplete="new-password"
        show-password
        :placeholder="t('auth.fields.password.placeholder')"
      />
    </el-form-item>
    <el-form-item :label="t('auth.ldap.userOu.label')" prop="config.ou">
      <el-input v-model="form.config.ou" :placeholder="t('auth.ldap.userOu.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.ldap.userFilter.label')" prop="config.ldap_filter">
      <el-input v-model="form.config.ldap_filter" :placeholder="t('auth.ldap.userFilter.placeholder')" />
    </el-form-item>
    <el-form-item :label="t('auth.ldap.attributeMapping.label')" prop="config.ldap_mapping">
      <el-input v-model="form.config.ldap_mapping" type="textarea" :rows="4" :placeholder="t('auth.ldap.attributeMapping.placeholder')" />
    </el-form-item>
    <el-form-item>
      <div class="flex-column">
        <span>{{ t('auth.enableAuthentication', { provider: LOGIN_METHOD.LDAP }) }}</span>
        <el-switch v-model="form.is_active" class="self-start" />
      </div>
    </el-form-item>
    <div>
      <!-- 保存 -->
      <el-button v-if="perm.system.chatAuth.edit()" type="primary" @click="submit('save')">{{ t('common.actions.save') }}</el-button>
      <!-- 测试连接 -->
      <el-button plain @click="submit('test')">{{ t('common.actions.testConnection') }}</el-button>
    </div>
  </el-form>
</template>
