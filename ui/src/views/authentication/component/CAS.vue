<template>
  <div class="p-24" v-loading="loading">
    <el-form
        ref="authFormRef"
        :rules="rules"
        :model="form"
        label-position="top"
        require-asterisk-position="right"
    >
      <el-form-item :label="$t('login.cas.ldpUri')" prop="config_data.ldpUri">
        <el-input v-model="form.config_data.ldpUri" :placeholder="$t('login.cas.ldpUriPlaceholder')"/>
      </el-form-item>
      <el-form-item :label="$t('login.cas.redirectUrl')" prop="config_data.redirectUrl">
        <el-input v-model="form.config_data.redirectUrl" :placeholder="$t('login.cas.redirectUrlPlaceholder')"/>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.is_active">{{ $t('login.cas.enableAuthentication') }}</el-checkbox>
      </el-form-item>
    </el-form>

    <div class="text-right">
      <el-button @click="submit(authFormRef)" type="primary" :disabled="loading"> {{ $t('login.cas.save') }}
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
  auth_type: 'CAS',
  config_data: {
    ldpUri: '',
    redirectUrl: '',
  },
  is_active: true
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config_data.ldpUri': [{required: true, message: t('login.ldap.ldpUriPlaceholder'), trigger: 'blur'}],
  'config_data.redirectUrl': [{
    required: true,
    message: t('login.ldap.redirectUrlPlaceholder'),
    trigger: 'blur'
  }],
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (test) {
        authApi.postAuthSetting(form.value, loading).then((res) => {
          MsgSuccess(t('login.cas.testConnectionSuccess'))
        })
      } else {
        authApi.putAuthSetting(form.value.auth_type, form.value, loading).then((res) => {
          MsgSuccess(t('login.cas.saveSuccess'))
        })
      }
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
