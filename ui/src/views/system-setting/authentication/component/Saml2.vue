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
              :label="$t('views.system.authentication.saml2.ldp')"
              prop="config.idpMetaUrl"
          >
            <el-input
                v-model="form.config.idpMetaUrl"
                :placeholder="$t('views.system.authentication.saml2.ldpPlaceholder')"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.config.wantAssertionsSigned">{{
                $t('views.system.authentication.saml2.enableAuthnRequests')
              }}
            </el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.config.wantAuthnRequestsSigned">{{
                $t('views.system.authentication.saml2.enableAssertions')
              }}
            </el-checkbox>
          </el-form-item>
          <el-form-item
              :label="$t('views.system.authentication.saml2.privateKey')"
              prop="config.privateKey"
          >
            <el-input
                v-model="form.config.privateKey"
                type="password"
                :placeholder="$t('views.system.authentication.saml2.privateKeyPlaceholder')"
            />
          </el-form-item>
          <el-form-item
              :label="$t('views.system.authentication.saml2.certificate')"
              prop="config.certificate"
          >
            <el-input
                v-model="form.config.certificate"
                type="password"
                :placeholder="$t('views.system.authentication.saml2.certificatePlaceholder')"
            />
          </el-form-item>

          <el-form-item :label="$t('views.system.authentication.saml2.filedMapping')"
                        prop="config.mapping">
            <el-input
                v-model="form.config.mapping"
                :placeholder="$t('views.system.authentication.saml2.filedMappingPlaceholder')"
            />
          </el-form-item>
          <el-form-item
              :label="$t('views.system.authentication.saml2.spEntityId')"
              prop="config.spEntityId"
          >
            <el-input
                v-model="form.config.spEntityId"
                :placeholder="$t('views.system.authentication.saml2.spEntityIdPlaceholder')"
            />
          </el-form-item>
          <el-form-item
              :label="$t('views.system.authentication.saml2.spAcs')"
              prop="config.spAcs"
          >
            <el-input
                v-model="form.config.spAcs"
                :placeholder="$t('views.system.authentication.saml2.spAcsPlaceholder')"
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="form.is_active">{{
                $t('views.system.authentication.saml2.enableAuthentication')
              }}
            </el-checkbox>
          </el-form-item>
        </el-form>

        <div>
          <span
              v-hasPermission="
              new ComplexPermission([RoleConst.ADMIN], [PermissionConst.LOGIN_AUTH_EDIT], [], 'OR')
            "
              class="mr-12"
          >
            <el-button @click="submit(authFormRef)" type="primary" :disabled="loading">
              {{ $t('common.save') }}
            </el-button>
          </span>
          <span>
            <el-button @click="submit(authFormRef, 'test')" :disabled="loading">
              {{ $t('views.system.test') }}</el-button
            >
          </span>
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
  auth_type: 'SAML2',
  config: {
    idpMetaUrl: '',
    wantAssertionsSigned: true,
    wantAuthnRequestsSigned: true,
    privateKey: '',
    certificate: '',
    mapping: '',
    spEntityId: window.location.origin + window.MaxKB.prefix + '/api/saml2/metadata',
    spAcs: window.location.origin + window.MaxKB.prefix + '/api/saml2/sso',
  },
  is_active: true,
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config.idpMetaUrl': [
    {
      required: true,
      message: t('views.system.authentication.saml2.ldpPlaceholder'),
      trigger: 'blur',
    },
  ],
  'config.privateKey': [
    {
      required: true,
      message: t('views.system.authentication.saml2.privateKeyPlaceholder'),
      trigger: 'blur',
    },
  ],
  'config.certificate': [
    {
      required: true,
      message: t('views.system.authentication.saml2.certificatePlaceholder'),
      trigger: 'blur',
    },
  ],
  'config.mapping': [
    {
      required: true,
      message: t('views.system.authentication.saml2.filedMappingPlaceholder'),
      trigger: 'blur',
    },
  ],
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
      if (res.data.config.mapping) {
        form.value.config.mapping = JSON.stringify(JSON.parse(res.data.config.mapping))
      }
      if (!form.value.config.spEntityId) {
        form.value.config.spEntityId = window.location.origin + window.MaxKB.prefix + '/api/saml2/metadata'
      }
      if (!form.value.config.spAcs) {
        form.value.config.spAcs = window.location.origin + window.MaxKB.prefix + '/api/saml2/sso'
      }
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
