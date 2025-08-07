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
            prop="config.authEndpoint"
          >
            <el-input
              v-model="form.config.authEndpoint"
              :placeholder="$t('views.system.authentication.oidc.authEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.tokenEndpoint')"
            prop="config.tokenEndpoint"
          >
            <el-input
              v-model="form.config.tokenEndpoint"
              :placeholder="$t('views.system.authentication.oidc.tokenEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.userInfoEndpoint')"
            prop="config.userInfoEndpoint"
          >
            <el-input
              v-model="form.config.userInfoEndpoint"
              :placeholder="$t('views.system.authentication.oidc.userInfoEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item label="Scope" prop="config.scope">
            <el-input v-model="form.config.scope" placeholder="openid+profile+email "/>
          </el-form-item>
          <el-form-item label="State" prop="config.state">
            <el-input v-model="form.config.state" placeholder=""/>
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.clientId')"
            prop="config.clientId"
          >
            <el-input
              v-model="form.config.clientId"
              :placeholder="$t('views.system.authentication.oidc.clientIdPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.clientSecret')"
            prop="config.clientSecret"
          >
            <el-input
              v-model="form.config.clientSecret"
              :placeholder="$t('views.system.authentication.oidc.clientSecretPlaceholder')"
              show-password
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oauth2.filedMapping')"
            prop="config.fieldMapping"
          >
            <el-input
              v-model="form.config.fieldMapping"
              :placeholder="$t('views.system.authentication.oauth2.filedMappingPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oidc.redirectUrl')"
            prop="config.redirectUrl"
          >
            <el-input
              v-model="form.config.redirectUrl"
              :placeholder="$t('views.system.authentication.oidc.redirectUrlPlaceholder')"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.is_active"
            >{{ $t('views.system.authentication.oidc.enableAuthentication') }}
            </el-checkbox>
          </el-form-item>
        </el-form>

        <div>
          <el-button @click="submit(authFormRef)" type="primary" :disabled="loading"
                     v-hasPermission="
                      new ComplexPermission(
                        [RoleConst.ADMIN],
                        [PermissionConst.LOGIN_AUTH_EDIT],
                        [],'OR',)"
          >
            {{ $t('common.save') }}
          </el-button>
        </div>
      </div>
    </el-scrollbar>
  </div>
</template>
<script setup lang="ts">
import {reactive, ref, watch, onMounted} from 'vue'
import authApi from '@/api/system-settings/auth-setting'
import type {FormInstance, FormRules} from 'element-plus'
import {t} from '@/locales'
import {MsgSuccess} from '@/utils/message'
import {PermissionConst, RoleConst} from '@/utils/permission/data'
import {ComplexPermission} from '@/utils/permission/type'

const form = ref<any>({
  id: '',
  auth_type: 'OIDC',
  config: {
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
  'config.authEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oidc.authEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.tokenEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oidc.tokenEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.userInfoEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oidc.userInfoEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.scope': [
    {
      required: true,
      message: t('views.system.authentication.oidc.scopePlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.clientId': [
    {
      required: true,
      message: t('views.system.authentication.oidc.clientIdPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.clientSecret': [
    {
      required: true,
      message: t('views.system.authentication.oidc.clientSecretPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.fieldMapping': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.filedMappingPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.redirectUrl': [
    {
      required: true,
      message: t('views.system.authentication.oidc.redirectUrlPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.logoutEndpoint': [
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
        form.value.config.fieldMapping === '' ||
        form.value.config.fieldMapping === undefined
      ) {
        form.value.config.fieldMapping = '{"username": "preferred_username", "email": "email"}'
      }
    }
    if (!form.value.config.redirectUrl) {
        form.value.config.redirectUrl = window.location.origin + window.MaxKB.prefix + '/api/oidc'
      }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
