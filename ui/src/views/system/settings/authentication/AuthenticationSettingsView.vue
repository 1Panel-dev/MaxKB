<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import AuthSettingApi from '@/api/admin/system/auth-setting'
import type { AuthProviderSetting, AuthProviderType, LoginAuthSetting } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

interface ProviderField {
  key: string
  label: string
  placeholder: string
  type?: 'password' | 'textarea'
}

interface ProviderDefinition {
  label: string
  type: AuthProviderType
  fields: ProviderField[]
}

const providerDefinitions: ProviderDefinition[] = [
  {
    label: 'LDAP',
    type: 'LDAP',
    fields: [
      { key: 'ldap_server', label: '服务器地址', placeholder: '请输入 LDAP 服务器地址' },
      { key: 'base_dn', label: 'Bind DN', placeholder: '请输入 Bind DN' },
      { key: 'password', label: '密码', placeholder: '请输入密码', type: 'password' },
      { key: 'ou', label: '用户目录', placeholder: '请输入用户目录' },
      { key: 'ldap_filter', label: '用户过滤器', placeholder: '请输入 LDAP 用户过滤器' },
      {
        key: 'ldap_mapping',
        label: '字段映射',
        placeholder: '请输入 JSON 格式的字段映射',
        type: 'textarea',
      },
    ],
  },
  {
    label: 'CAS',
    type: 'CAS',
    fields: [
      { key: 'service', label: 'CAS 服务地址', placeholder: '请输入 CAS 服务地址' },
      { key: 'validate_url', label: '校验地址', placeholder: '请输入校验地址' },
      { key: 'redirect_url', label: '回调地址', placeholder: '请输入回调地址' },
    ],
  },
  {
    label: 'OIDC',
    type: 'OIDC',
    fields: [
      { key: 'auth_endpoint', label: '授权端点', placeholder: '请输入授权端点' },
      { key: 'token_endpoint', label: 'Token 端点', placeholder: '请输入 Token 端点' },
      { key: 'userinfo_endpoint', label: '用户信息端点', placeholder: '请输入用户信息端点' },
      { key: 'scope', label: 'Scope', placeholder: '请输入 Scope' },
      { key: 'client_id', label: 'Client ID', placeholder: '请输入 Client ID' },
      {
        key: 'client_secret',
        label: 'Client Secret',
        placeholder: '请输入 Client Secret',
        type: 'password',
      },
      {
        key: 'mapping',
        label: '字段映射',
        placeholder: '请输入 JSON 格式的字段映射',
        type: 'textarea',
      },
      { key: 'redirect_url', label: '回调地址', placeholder: '请输入回调地址' },
    ],
  },
  {
    label: 'OAuth2',
    type: 'OAuth2',
    fields: [
      { key: 'auth_endpoint', label: '授权端点', placeholder: '请输入授权端点' },
      { key: 'token_endpoint', label: 'Token 端点', placeholder: '请输入 Token 端点' },
      { key: 'userinfo_endpoint', label: '用户信息端点', placeholder: '请输入用户信息端点' },
      { key: 'scope', label: 'Scope', placeholder: '请输入 Scope' },
      { key: 'client_id', label: 'Client ID', placeholder: '请输入 Client ID' },
      {
        key: 'client_secret',
        label: 'Client Secret',
        placeholder: '请输入 Client Secret',
        type: 'password',
      },
      {
        key: 'mapping',
        label: '字段映射',
        placeholder: '请输入 JSON 格式的字段映射',
        type: 'textarea',
      },
      { key: 'redirect_url', label: '回调地址', placeholder: '请输入回调地址' },
    ],
  },
  {
    label: 'SAML2',
    type: 'SAML2',
    fields: [
      { key: 'idp', label: 'Identity Provider', placeholder: '请输入 Identity Provider 地址' },
      { key: 'private_key', label: '私钥', placeholder: '请输入私钥', type: 'textarea' },
      { key: 'certificate', label: '证书', placeholder: '请输入证书', type: 'textarea' },
      {
        key: 'mapping',
        label: '字段映射',
        placeholder: '请输入 JSON 格式的字段映射',
        type: 'textarea',
      },
      { key: 'sp_entity_id', label: 'SP Entity ID', placeholder: '请输入 SP Entity ID' },
      { key: 'sp_acs', label: 'SP ACS', placeholder: '请输入 SP ACS 地址' },
    ],
  },
]

const defaultLoginSetting: LoginAuthSetting = {
  default_value: 'LOCAL',
  failed_attempts: 5,
  lock_time: 10,
  login_methods: ['LOCAL'],
  max_attempts: 1,
}

const activeTab = ref('LOGIN')
const loading = ref(false)
const loginFormRef = useTemplateRef<FormInstance>('loginFormRef')
const providerFormRef = useTemplateRef<FormInstance>('providerFormRef')
const loginSetting = reactive<LoginAuthSetting>({ ...defaultLoginSetting })
const providerSetting = reactive<AuthProviderSetting>({
  auth_type: 'LDAP',
  config: {},
  is_active: false,
})
const currentProvider = computed(() =>
  providerDefinitions.find(({ type }) => type === activeTab.value),
)
const loginMethodOptions = computed(() => loginSetting.system_options ?? [])
const providerRules = computed<FormRules>(() =>
  Object.fromEntries(
    (currentProvider.value?.fields ?? []).map(({ key, label }) => [
      `config.${key}`,
      [{ required: true, message: `请输入${label}`, trigger: 'blur' }],
    ]),
  ),
)

/* 登录设置加载与提交 */
function loadLoginSetting() {
  loading.value = true
  return AuthSettingApi.getLoginSetting()
    .then((setting) => Object.assign(loginSetting, defaultLoginSetting, setting))
    .finally(() => {
      loading.value = false
    })
}

function submitLoginSetting() {
  loginFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    AuthSettingApi.putLoginSetting(loginSetting)
      .then(() => MsgSuccess('保存成功'))
      .finally(() => {
        loading.value = false
      })
  })
}

/* 认证源加载、测试与提交 */
function loadProviderSetting(authType: AuthProviderType) {
  loading.value = true
  return AuthSettingApi.getAuthSetting(authType)
    .then((setting) =>
      Object.assign(
        providerSetting,
        { auth_type: authType, config: {}, is_active: false },
        setting,
      ),
    )
    .finally(() => {
      loading.value = false
    })
}

function submitProviderSetting(action: 'save' | 'test') {
  providerFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    const request =
      action === 'test'
        ? AuthSettingApi.postAuthSettingConnection(providerSetting)
        : AuthSettingApi.putAuthSetting(providerSetting.auth_type, providerSetting)
    request
      .then(() => MsgSuccess(action === 'test' ? '连接成功' : '保存成功'))
      .finally(() => {
        loading.value = false
      })
  })
}

watch(activeTab, (tab) => {
  if (tab !== 'LOGIN') loadProviderSetting(tab as AuthProviderType)
})

onMounted(loadLoginSetting)
</script>

<template>
  <MkViewLayout v-loading="loading">
    <el-tabs v-model="activeTab" class="h-full">
      <el-tab-pane label="登录设置" name="LOGIN">
        <el-form ref="loginFormRef" class="max-w-3xl" :model="loginSetting" label-position="top">
          <el-form-item label="允许的登录方式" prop="login_methods" required>
            <el-checkbox-group v-model="loginSetting.login_methods">
              <el-checkbox
                v-for="option in loginMethodOptions"
                :key="option.value"
                :label="option.value"
              >
                {{ option.label }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="默认登录方式" prop="default_value" required>
            <el-select v-model="loginSetting.default_value" class="w-full">
              <el-option
                v-for="option in loginMethodOptions.filter(({ value }) =>
                  loginSetting.login_methods.includes(value),
                )"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
          <div class="grid grid-cols-3 gap-4">
            <el-form-item label="最大并发登录数">
              <el-input-number v-model="loginSetting.max_attempts" :min="-1" />
            </el-form-item>
            <el-form-item label="登录失败锁定次数">
              <el-input-number v-model="loginSetting.failed_attempts" :min="-1" />
            </el-form-item>
            <el-form-item label="锁定时间（分钟）">
              <el-input-number v-model="loginSetting.lock_time" :min="1" />
            </el-form-item>
          </div>
          <el-button type="primary" @click="submitLoginSetting">保存</el-button>
        </el-form>
      </el-tab-pane>

      <el-tab-pane
        v-for="provider in providerDefinitions"
        :key="provider.type"
        :label="provider.label"
        :name="provider.type"
      >
        <el-scrollbar class="h-full">
          <el-form
            v-if="currentProvider?.type === provider.type"
            ref="providerFormRef"
            class="max-w-3xl"
            :model="providerSetting"
            :rules="providerRules"
            label-position="top"
          >
            <el-form-item
              v-for="field in provider.fields"
              :key="field.key"
              :label="field.label"
              :prop="`config.${field.key}`"
            >
              <el-input
                v-model="providerSetting.config[field.key]"
                :placeholder="field.placeholder"
                :rows="field.type === 'textarea' ? 4 : undefined"
                :show-password="field.type === 'password'"
                :type="field.type ?? 'text'"
              />
            </el-form-item>
            <el-form-item>
              <el-switch v-model="providerSetting.is_active" />
              <span class="ml-2">启用认证</span>
            </el-form-item>
            <div class="flex gap-3">
              <el-button type="primary" @click="submitProviderSetting('save')">保存</el-button>
              <el-button v-if="provider.type === 'LDAP'" @click="submitProviderSetting('test')">
                测试连接
              </el-button>
            </div>
          </el-form>
        </el-scrollbar>
      </el-tab-pane>
    </el-tabs>
  </MkViewLayout>
</template>
