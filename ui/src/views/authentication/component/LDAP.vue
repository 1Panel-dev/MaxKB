<template>
  <div class="p-24" v-loading="loading">
    <el-form
        ref="authFormRef"
        :rules="rules"
        :model="form"
        label-position="top"
        require-asterisk-position="right"
    >
      <el-form-item :label="$t('login.ldap.address')" prop="config_data.ldap_server">
        <el-input v-model="form.config_data.ldap_server" :placeholder="$t('login.ldap.serverPlaceholder')"/>
      </el-form-item>
      <el-form-item :label="$t('login.ldap.bindDN')" prop="config_data.base_dn">
        <el-input v-model="form.config_data.base_dn" :placeholder="$t('login.ldap.bindDNPlaceholder')"/>
      </el-form-item>
      <el-form-item :label="$t('login.ldap.password')" prop="config_data.password">
        <el-input v-model="form.config_data.password" :placeholder="$t('login.ldap.passwordPlaceholder')"
                  show-password/>
      </el-form-item>
      <el-form-item :label="$t('login.ldap.ou')" prop="config_data.ou">
        <el-input v-model="form.config_data.ou" :placeholder="$t('login.ldap.ouPlaceholder')"/>
      </el-form-item>
      <el-form-item :label="$t('login.ldap.ldap_filter')" prop="config_data.ldap_filter">
        <el-input v-model="form.config_data.ldap_filter" :placeholder="$t('login.ldap.ldap_filterPlaceholder')"/>
      </el-form-item>
      <el-form-item :label="$t('login.ldap.ldap_mapping')" prop="config_data.ldap_mapping">
        <el-input v-model="form.config_data.ldap_mapping" placeholder='{"name":"name","email":"mail","username":"cn"}'/>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.is_active">{{ $t('login.ldap.enableAuthentication') }}</el-checkbox>
      </el-form-item>
      <el-button @click="submit(authFormRef, 'test')" :disabled="loading"> {{ $t('login.ldap.test') }}</el-button>
    </el-form>

    <div class="text-right">
      <el-button @click="submit(authFormRef)" type="primary" :disabled="loading"> {{ $t('login.ldap.save') }}
      </el-button>
    </div>
  </div>
</template>
<script setup lang="ts">
import {reactive, ref, watch, onMounted} from 'vue'
import authApi from '@/api/auth-setting'
import type {FormInstance, FormRules} from 'element-plus'
import {t} from '@/locales'
import {MsgSuccess} from '@/utils/message'

const form = ref<any>({
  id: '',
  auth_type: 'LDAP',
  config_data: {
    ldap_server: '',
    base_dn: '',
    password: '',
    ou: '',
    ldap_filter: '',
    ldap_mapping: '',
  },
  is_active: true
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config_data.ldap_server': [{required: true, message: t('login.ldap.serverPlaceholder'), trigger: 'blur'}],
  'config_data.base_dn': [{required: true, message: t('login.ldap.bindDNPlaceholder'), trigger: 'blur'}],
  'config_data.password': [{required: true, message: t('login.ldap.passwordPlaceholder'), trigger: 'blur'}],
  'config_data.ou': [{required: true, message: t('login.ldap.ouPlaceholder'), trigger: 'blur'}],
  'config_data.ldap_filter': [{required: true, message: t('login.ldap.ldap_filterPlaceholder'), trigger: 'blur'}],
  'config_data.ldap_mapping': [{required: true, message: t('login.ldap.ldap_mappingPlaceholder'), trigger: 'blur'}]
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (test) {
        authApi.postAuthSetting(form.value, loading).then((res) => {
          MsgSuccess(t('login.ldap.testConnectionSuccess'))
        })
      } else {
        authApi.putAuthSetting(form.value.auth_type, form.value, loading).then((res) => {
          MsgSuccess(t('login.ldap.saveSuccess'))
        })
      }
    }
  })
}

function getDetail() {
  authApi.getAuthSetting(form.value.auth_type, loading).then((res: any) => {
    if (res.data && JSON.stringify(res.data) !== '{}') {
      form.value = res.data
      if (res.data.config_data.ldap_mapping) {
        form.value.config_data.ldap_mapping = JSON.stringify(JSON.parse(res.data.config_data.ldap_mapping))
      }
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
