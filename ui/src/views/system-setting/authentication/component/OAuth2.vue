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
            :label="$t('views.system.authentication.oauth2.authEndpoint')"
            prop="config.authEndpoint"
          >
            <el-input
              v-model="form.config.authEndpoint"
              :placeholder="$t('views.system.authentication.oauth2.authEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oauth2.tokenEndpoint')"
            prop="config.tokenEndpoint"
          >
            <el-input
              v-model="form.config.tokenEndpoint"
              :placeholder="$t('views.system.authentication.oauth2.tokenEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oauth2.userInfoEndpoint')"
            prop="config.userInfoEndpoint"
          >
            <el-input
              v-model="form.config.userInfoEndpoint"
              :placeholder="$t('views.system.authentication.oauth2.userInfoEndpointPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oauth2.scope')"
            prop="config.scope"
          >
            <el-input
              v-model="form.config.scope"
              :placeholder="$t('views.system.authentication.oauth2.scopePlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oauth2.clientId')"
            prop="config.clientId"
          >
            <el-input
              v-model="form.config.clientId"
              :placeholder="$t('views.system.authentication.oauth2.clientIdPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.oauth2.clientSecret')"
            prop="config.clientSecret"
          >
            <el-input
              v-model="form.config.clientSecret"
              :placeholder="$t('views.system.authentication.oauth2.clientSecretPlaceholder')"
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
            :label="$t('views.system.authentication.oauth2.redirectUrl')"
            prop="config.redirectUrl"
          >
            <el-input
              v-model="form.config.redirectUrl"
              :placeholder="$t('views.system.authentication.oauth2.redirectUrlPlaceholder')"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.is_active"
            >{{ $t('views.system.authentication.oauth2.enableAuthentication') }}
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
import {reactive, ref, onMounted} from 'vue'
import authApi from '@/api/system-settings/auth-setting'
import type {FormInstance, FormRules} from 'element-plus'
import {t} from '@/locales'
import {MsgSuccess} from '@/utils/message'
import {PermissionConst, RoleConst} from '@/utils/permission/data'
import {ComplexPermission} from '@/utils/permission/type'

const form = ref<any>({
  id: '',
  auth_type: 'OAuth2',
  config: {
    authEndpoint: '',
    tokenEndpoint: '',
    userInfoEndpoint: '',
    scope: '',
    clientId: '',
    clientSecret: '',
    redirectUrl: '',
    fieldMapping: ''
  },
  is_active: true
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config.authEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.authEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.tokenEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.tokenEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.userInfoEndpoint': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.userInfoEndpointPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.scope': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.scopePlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.clientId': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.clientIdPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.clientSecret': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.clientSecretPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.redirectUrl': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.redirectUrlPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.fieldMapping': [
    {
      required: true,
      message: t('views.system.authentication.oauth2.filedMappingPlaceholder'),
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
    }
    if (!form.value.config.redirectUrl) {
      form.value.config.redirectUrl = window.location.origin + window.MaxKB.prefix + '/api/oauth2'
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
