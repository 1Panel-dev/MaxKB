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
            :label="$t('views.system.authentication.cas.ldpUri')"
            prop="config_data.ldpUri"
          >
            <el-input
              v-model="form.config_data.ldpUri"
              :placeholder="$t('views.system.authentication.cas.ldpUriPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.cas.validateUrl')"
            prop="config_data.validateUrl"
          >
            <el-input
              v-model="form.config_data.validateUrl"
              :placeholder="$t('views.system.authentication.cas.validateUrlPlaceholder')"
            />
          </el-form-item>
          <el-form-item
            :label="$t('views.system.authentication.cas.redirectUrl')"
            prop="config_data.redirectUrl"
          >
            <el-input
              v-model="form.config_data.redirectUrl"
              :placeholder="$t('views.system.authentication.cas.redirectUrlPlaceholder')"
            />
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="form.is_active"
              >{{ $t('views.system.authentication.cas.enableAuthentication') }}
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
  auth_type: 'CAS',
  config_data: {
    ldpUri: '',
    validateUrl: '',
    redirectUrl: ''
  },
  is_active: true
})

const authFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  'config_data.ldpUri': [
    {
      required: true,
      message: t('views.system.authentication.cas.ldpUriPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.validateUrl': [
    {
      required: true,
      message: t('views.system.authentication.cas.validateUrlPlaceholder'),
      trigger: 'blur'
    }
  ],
  'config_data.redirectUrl': [
    {
      required: true,
      message: t('views.system.authentication.cas.redirectUrlPlaceholder'),
      trigger: 'blur'
    }
  ]
})

const submit = async (formEl: FormInstance | undefined) => {
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
      if (!res.data.config_data.validateUrl) {
        res.data.config_data.validateUrl = res.data.config_data.ldpUri
      }
      form.value = res.data
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped></style>
