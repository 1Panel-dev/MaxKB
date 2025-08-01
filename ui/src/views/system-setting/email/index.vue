<template>
  <div class="email-setting p-16-24">
    <el-breadcrumb separator-icon="ArrowRight" class="mb-16">
      <el-breadcrumb-item>{{ t('views.system.subTitle') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ $t('views.system.email.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card style="--el-card-padding: 16px" v-loading="loading">
      <el-scrollbar>
        <div class="email-setting__main p-16">
          <el-form
            ref="emailFormRef"
            :rules="rules"
            :model="form"
            label-position="top"
            require-asterisk-position="right"
          >
            <el-form-item :label="$t('views.system.email.smtpHost')" prop="email_host">
              <el-input
                v-model="form.email_host"
                :placeholder="$t('views.system.email.smtpHostPlaceholder')"
              />
            </el-form-item>
            <el-form-item :label="$t('views.system.email.smtpPort')" prop="email_port">
              <el-input
                v-model="form.email_port"
                :placeholder="$t('views.system.email.smtpPortPlaceholder')"
              />
            </el-form-item>
            <el-form-item :label="$t('views.system.email.smtpUser')" prop="email_host_user">
              <el-input
                v-model="form.email_host_user"
                :placeholder="$t('views.system.email.smtpUserPlaceholder')"
              />
            </el-form-item>
            <el-form-item :label="$t('views.system.email.sendEmail')" prop="from_email">
              <el-input
                v-model="form.from_email"
                :placeholder="$t('views.system.email.sendEmailPlaceholder')"
              />
            </el-form-item>
            <el-form-item :label="$t('views.system.password')" prop="email_host_password">
              <el-input
                v-model="form.email_host_password"
                :placeholder="$t('views.system.email.smtpPasswordPlaceholder')"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.email_use_ssl"
                >{{ $t('views.system.email.enableSSL') }}
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.email_use_tls"
                >{{ $t('views.system.email.enableTLS') }}
              </el-checkbox>
            </el-form-item>
            <el-button
              @click="submit(emailFormRef)"
              type="primary"
              :disabled="loading"
              v-hasPermission="
                new ComplexPermission(
                  [RoleConst.ADMIN],
                  [PermissionConst.EMAIL_SETTING_EDIT],
                  [],
                  'OR',
                )
              "
            >
              {{ $t('common.save') }}
            </el-button>
            <el-button @click="submit(emailFormRef, 'test')" :disabled="loading">
              {{ $t('views.system.test') }}
            </el-button>
          </el-form>
        </div>
      </el-scrollbar>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import emailApi from '@/api/system-settings/email-setting'
import type { FormInstance, FormRules } from 'element-plus'

import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'

const form = ref<any>({
  email_host: '',
  email_port: '',
  email_host_user: '',
  email_host_password: '',
  email_use_tls: false,
  email_use_ssl: false,
  from_email: '',
})

const emailFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  email_host: [
    { required: true, message: t('views.system.email.smtpHostPlaceholder'), trigger: 'blur' },
  ],
  email_port: [
    { required: true, message: t('views.system.email.smtpPortPlaceholder'), trigger: 'blur' },
  ],
  email_host_user: [
    { required: true, message: t('views.system.email.smtpUserPlaceholder'), trigger: 'blur' },
  ],
  email_host_password: [
    { required: true, message: t('views.system.email.smtpPasswordPlaceholder'), trigger: 'blur' },
  ],
  from_email: [
    { required: true, message: t('views.system.email.sendEmailPlaceholder'), trigger: 'blur' },
  ],
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (test) {
        emailApi.postTestEmail(form.value, loading).then((res) => {
          MsgSuccess(t('views.system.testSuccess'))
        })
      } else {
        emailApi.putEmailSetting(form.value, loading).then((res) => {
          MsgSuccess(t('common.saveSuccess'))
        })
      }
    }
  })
}

function getDetail() {
  emailApi.getEmailSetting(loading).then((res: any) => {
    if (res.data && JSON.stringify(res.data) !== '{}') {
      form.value = res.data
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped>
.email-setting {
  &__main {
    width: 70%;
    margin: 0 auto;
    height: calc(100vh - 200px);
  }

  :deep(.el-checkbox__label) {
    font-weight: 400;
  }
}
</style>
