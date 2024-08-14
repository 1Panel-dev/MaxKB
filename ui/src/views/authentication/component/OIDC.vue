<template>
  <div class="p-24" v-loading="loading">
    <el-form
      ref="authFormRef"
      :rules="rules"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item :label="$t('login.oidc.authEndpoint')" prop="config_data.authEndpoint">
        <el-input
          v-model="form.config_data.authEndpoint"
          :placeholder="$t('login.oidc.authEndpointPlaceholder')"
        />
      </el-form-item>
      <el-form-item :label="$t('login.oidc.tokenEndpoint')" prop="config_data.tokenEndpoint">
        <el-input
          v-model="form.config_data.tokenEndpoint"
          :placeholder="$t('login.oidc.tokenEndpointPlaceholder')"
        />
      </el-form-item>
      <el-form-item :label="$t('login.oidc.userInfoEndpoint')" prop="config_data.userInfoEndpoint">
        <el-input
          v-model="form.config_data.userInfoEndpoint"
          :placeholder="$t('login.oidc.userInfoEndpointPlaceholder')"
        />
      </el-form-item>
      <el-form-item :label="$t('login.oidc.clientId')" prop="config_data.clientId">
        <el-input
          v-model="form.config_data.clientId"
          :placeholder="$t('login.oidc.clientIdPlaceholder')"
        />
      </el-form-item>
      <el-form-item :label="$t('login.oidc.clientSecret')" prop="config_data.clientSecret">
        <el-input
          v-model="form.config_data.clientSecret"
          :placeholder="$t('login.oidc.clientSecretPlaceholder')"
          show-password
        />
      </el-form-item>
      <el-form-item :label="$t('login.oidc.redirectUrl')" prop="config_data.redirectUrl">
        <el-input
          v-model="form.config_data.redirectUrl"
          :placeholder="$t('login.oidc.redirectUrlPlaceholder')"
        />
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.is_active"
          >{{ $t('login.oidc.enableAuthentication') }}
        </el-checkbox>
      </el-form-item>
    </el-form>

    <div class="text-right">
      <el-button @click="submit(authFormRef)" type="primary" :disabled="loading">
        {{ $t('login.ldap.save') }}
      </el-button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import authApi from '@/api/auth-setting'
import type { FormInstance, FormRules } from 'element-plus'
import { t } from '@/locales'
import { MsgSuccess } from '@/utils/message'

const form = ref<any>({
  id: '',
  auth_type: 'OIDC',
  config_data: {
    authEndpoint: '',
    tokenEndpoint: '',
    userInfoEndpoint: '',
    clientId: '',
    clientSecret: '',
    redirectUrl: ''
  },
  is_active: true
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config_data.authEndpoint': [
    { required: true, message: t('login.oidc.authEndpointPlaceholder'), trigger: 'blur' }
  ],
  'config_data.tokenEndpoint': [
    { required: true, message: t('login.oidc.tokenEndpointPlaceholder'), trigger: 'blur' }
  ],
  'config_data.userInfoEndpoint': [
    {
      required: true,
      message: t('login.oidc.userInfoEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.clientId': [
    { required: true, message: t('login.oidc.clientIdPlaceholder'), trigger: 'blur' }
  ],
  'config_data.clientSecret': [
    { required: true, message: t('login.oidc.clientSecretPlaceholder'), trigger: 'blur' }
  ],
  'config_data.redirectUrl': [
    { required: true, message: t('login.oidc.redirectUrlPlaceholder'), trigger: 'blur' }
  ],
  'config_data.logoutEndpoint': [
    { required: true, message: t('login.oidc.logoutEndpointPlaceholder'), trigger: 'blur' }
  ]
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      authApi.putAuthSetting(form.value.auth_type, form.value, loading).then((res) => {
        MsgSuccess(t('login.ldap.saveSuccess'))
      })
    }
  })
}

function getDetail() {
  authApi.getAuthSetting(form.value.auth_type, loading).then((res: any) => {
    if (res.data && JSON.stringify(res.data) !== '{}') {
      form.value = res.data
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
