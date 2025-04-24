<template>
  <div class="authentication-setting__main main-calc-height">
    <el-scrollbar>
      <div class="form-container p-24" v-loading="loading">
        <el-form
          ref="authFormRef"
          :rules="rules"
          :model="form"
          label-position="top"
          require-asterisk-position="right"
        >
          <el-form-item
            :label="$t('views.system.authentication.oidc.authEndpoint')"
            prop="config_data.authEndpoint"
          >
            <el-input
              v-model="form.config_data.authEndpoint"
              :placeholder="$t('views.system.authentication.oidc.authEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.tokenEndpoint')"
            prop="config_data.tokenEndpoint"
          >
            <el-input
              v-model="form.config_data.tokenEndpoint"
              :placeholder="$t('views.system.authentication.oidc.tokenEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.userInfoEndpoint')"
            prop="config_data.userInfoEndpoint"
          >
            <el-input
              v-model="form.config_data.userInfoEndpoint"
              :placeholder="$t('views.system.authentication.oidc.userInfoEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item label="Scope" prop="config_data.scope">
            <el-input v-model="form.config_data.scope" placeholder="openid+profile+email " />
          </el-form-item>
          <el-form-item label="State" prop="config_data.state">
            <el-input v-model="form.config_data.state" placeholder="" />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.clientId')"
            prop="config_data.clientId"
          >
            <el-input
              v-model="form.config_data.clientId"
              :placeholder="$t('views.system.authentication.oidc.clientIdPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.clientSecret')"
            prop="config_data.clientSecret"
          >
            <el-input
              v-model="form.config_data.clientSecret"
              :placeholder="$t('views.system.authentication.oidc.clientSecretPlaceholder')"
              show-password
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oauth2.filedMapping')"
            prop="config_data.fieldMapping"
          >
            <el-input
              v-model="form.config_data.fieldMapping"
              :placeholder="$t('views.system.authentication.oauth2.filedMappingPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.redirectUrl')"
            prop="config_data.redirectUrl"
          >
            <el-input
              v-model="form.config_data.redirectUrl"
              :placeholder="$t('views.system.authentication.oidc.redirectUrlPlaceholder')"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.is_active"
              >{{ $t('views.system.authentication.oidc.enableAuthentication') }}
            </el-checkbox>
          </el-form-item>
        </el-form>

        <div class="text-right">
          <el-button @click="submit(authFormRef)" type="primary" :disabled="loading">
            {{ $t('common.save') }}
          </el-button>
        </div>
      </div>
    </el-scrollbar>
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
    scope: '',
    state: '',
    clientId: '',
    clientSecret: '',
    fieldMapping: '{"username": "preferred_username", "email": "email"}',
    redirectUrl: ''
  },
  is_active: true
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config_data.authEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oidc.authEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.tokenEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oidc.tokenEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.userInfoEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oidc.userInfoEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.scope': [
    {
      required: true,
      message: t('views.system.authentication.oidc.scopePlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.clientId': [
    {
      required: true,
      message: t('views.system.authentication.oidc.clientIdPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.clientSecret': [
    {
      required: true,
      message: t('views.system.authentication.oidc.clientSecretPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.fieldMapping': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.filedMappingPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.redirectUrl': [
    {
      required: true,
      message: t('views.system.authentication.oidc.redirectUrlPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.logoutEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oidc.logoutEndpointPlaceholder'),
      trigger: 'blur'
    }
  ]
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      authApi.putAuthSetting(form.value.auth_type, form.value, loading).then((res) => {
        MsgSuccess(t('common.saveSuccess'))
      })
    }
  })
}

function getDetail() {
  authApi.getAuthSetting(form.value.auth_type, loading).then((res: any) => {
    if (res.data && JSON.stringify(res.data) !== '{}') {
      form.value = res.data
      if (
        form.value.config_data.fieldMapping === '' ||
        form.value.config_data.fieldMapping === undefined
      ) {
        form.value.config_data.fieldMapping = '{"username": "preferred_username", "email": "email"}'
      }
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
