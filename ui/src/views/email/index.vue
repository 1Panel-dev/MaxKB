<template>
  <LayoutContainer header="邮箱配置">
    <div class="email-setting main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <el-form
            ref="emailFormRef"
            :rules="rules"
            :model="form"
            label-position="top"
            require-asterisk-position="right"
          >
            <el-form-item label="SMTP 主机" prop="email_host">
              <el-input v-model="form.email_host" placeholder="请输入 SMTP 主机" />
            </el-form-item>
            <el-form-item label="SMTP 端口" prop="email_port">
              <el-input v-model="form.email_port" placeholder="请输入 SMTP 端口" />
            </el-form-item>
            <el-form-item label="SMTP 账户" prop="email_host_user">
              <el-input v-model="form.email_host_user" placeholder="请输入 SMTP 账户" />
            </el-form-item>
            <el-form-item label="发件人邮箱" prop="from_email">
              <el-input v-model="form.from_email" placeholder="请输入发件人邮箱" />
            </el-form-item>
            <el-form-item label="密码" prop="email_host_password">
              <el-input
                v-model="form.email_host_password"
                placeholder="请输入发件人密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.email_use_ssl"
                >开启SSL(如果SMTP端口是465，通常需要启用SSL)
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.email_use_tls"
                >开启TLS(如果SMTP端口是587，通常需要启用TLS)</el-checkbox
              >
            </el-form-item>
            <el-button @click="submit(emailFormRef, 'test')" :disabled="loading">
              测试连接
            </el-button>
          </el-form>

          <div class="text-right">
            <el-button @click="submit(emailFormRef)" type="primary" :disabled="loading">
              保存
            </el-button>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import emailApi from '@/api/email-setting'
import type { FormInstance, FormRules } from 'element-plus'

import { MsgSuccess } from '@/utils/message'
const form = ref<any>({
  email_host: '',
  email_port: '',
  email_host_user: '',
  email_host_password: '',
  email_use_tls: false,
  email_use_ssl: false,
  from_email: ''
})

const emailFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  email_host: [{ required: true, message: '请输入 SMTP 主机', trigger: 'blur' }],
  email_port: [{ required: true, message: '请输入 SMTP 端口', trigger: 'blur' }],
  email_host_user: [{ required: true, message: '请输入 SMTP 账户', trigger: 'blur' }],
  email_host_password: [{ required: true, message: '请输入发件人邮箱密码', trigger: 'blur' }],
  from_email: [{ required: true, message: '请输入发件人邮箱', trigger: 'blur' }]
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (test) {
        emailApi.postTestEmail(form.value, loading).then((res) => {
          MsgSuccess('测试连接成功')
        })
      } else {
        emailApi.putEmailSetting(form.value, loading).then((res) => {
          MsgSuccess('设置成功')
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
  width: 70%;
  margin: 0 auto;
  :deep(.el-checkbox__label) {
    font-weight: 400;
  }
}
</style>
