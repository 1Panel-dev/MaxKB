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
            :label="$t('views.system.authentication.ldap.address')"
            prop="config.ldap_server"
          >
            <el-input
              v-model="form.config.ldap_server"
              :placeholder="$t('views.system.authentication.ldap.serverPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.ldap.bindDN')"
            prop="config.base_dn"
          >
            <el-input
              v-model="form.config.base_dn"
              :placeholder="$t('views.system.authentication.ldap.bindDNPlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="$t('views.system.password')" prop="config.password">
            <el-input
              v-model="form.config.password"
              :placeholder="$t('views.login.loginForm.password.placeholder')"
              show-password
            />
          </el-form-item>
          <el-form-item :label="$t('views.system.authentication.ldap.ou')" prop="config.ou">
            <el-input
              v-model="form.config.ou"
              :placeholder="$t('views.system.authentication.ldap.ouPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.ldap.ldap_filter')"
            prop="config.ldap_filter"
          >
            <el-input
              v-model="form.config.ldap_filter"
              :placeholder="$t('views.system.authentication.ldap.ldap_filterPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.ldap.ldap_mapping')"
            prop="config.ldap_mapping"
          >
            <el-input
              v-model="form.config.ldap_mapping"
              placeholder='{"name":"name","email":"mail","username":"cn"}'
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.is_active">{{
              $t('views.system.authentication.ldap.enableAuthentication')
            }}</el-checkbox>
          </el-form-item>
        </el-form>

        <div>
          <el-button @click="submit(authFormRef, 'test')" :disabled="loading">
            {{ $t('views.system.test') }}</el-button
          >
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
import { reactive, ref, watch, onMounted } from 'vue'
import authApi from '@/api/system-settings/auth-setting'
import type { FormInstance, FormRules } from 'element-plus'
import { t } from '@/locales'
import { MsgSuccess } from '@/utils/message'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'

const form = ref<any>({
  id: '',
  auth_type: 'LDAP',
  config: {
    ldap_server: '',
    base_dn: '',
    password: '',
    ou: '',
    ldap_filter: '',
    ldap_mapping: ''
  },
  is_active: true
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config.ldap_server': [
    {
      required: true,
      message: t('views.system.authentication.ldap.serverPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.base_dn': [
    {
      required: true,
      message: t('views.system.authentication.ldap.bindDNPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.password': [
    {
      required: true,
      message: t('views.login.loginForm.password.placeholder'),
      trigger: 'blur'
    }
  ],
  'config.ou': [
    {
      required: true,
      message: t('views.system.authentication.ldap.ouPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.ldap_filter': [
    {
      required: true,
      message: t('views.system.authentication.ldap.ldap_filterPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config.ldap_mapping': [
    {
      required: true,
      message: t('views.system.authentication.ldap.ldap_mappingPlaceholder'),
      trigger: 'blur'
    }
  ]
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (test) {
        authApi.postAuthSetting(form.value, loading).then((res) => {
          MsgSuccess(t('views.system.testSuccess'))
        })
      } else {
        authApi.putAuthSetting(form.value.auth_type, form.value, loading).then((res) => {
          MsgSuccess(t('common.saveSuccess'))
        })
      }
    }
  })
}

function getDetail() {
  authApi.getAuthSetting(form.value.auth_type, loading).then((res: any) => {
    if (res.data && JSON.stringify(res.data) !== '{}') {
      form.value = res.data
      if (res.data.config.ldap_mapping) {
        form.value.config.ldap_mapping = JSON.stringify(
          JSON.parse(res.data.config.ldap_mapping)
        )
      }
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
