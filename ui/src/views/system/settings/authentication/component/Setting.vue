<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import AuthSettingApi from '@/api/admin/system/auth-setting'
import type { LoginAuthSetting } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'LoginAuthenticationSetting' })

const defaultSetting: LoginAuthSetting = {
  default_value: 'LOCAL',
  failed_attempts: 5,
  lock_time: 10,
  login_methods: ['LOCAL'],
  max_attempts: 1,
}

const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<LoginAuthSetting>({ ...defaultSetting })
const loginMethodOptions = computed(() => form.system_options ?? form.auth_types ?? [])
const selectedLoginMethodOptions = computed(() =>
  loginMethodOptions.value.filter(({ value }) => form.login_methods.includes(value)),
)
const rules: FormRules<LoginAuthSetting> = {
  default_value: [{ required: true, message: '请选择默认登录方式', trigger: 'change' }],
  login_methods: [{ required: true, message: '请至少选择一种登录方式', trigger: 'change' }],
}

/* 登录方式加载与提交 */
function loadSetting() {
  loading.value = true
  return AuthSettingApi.getLoginSetting()
    .then((setting) => Object.assign(form, defaultSetting, setting))
    .finally(() => {
      loading.value = false
    })
}

function normalizeAttemptCount(value: number | undefined) {
  if (value === undefined || value === 0) return 1
  return Math.max(-1, Math.trunc(value))
}

function submit() {
  authFormRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    AuthSettingApi.putLoginSetting(form)
      .then(() => MsgSuccess('保存成功'))
      .finally(() => {
        loading.value = false
      })
  })
}

watch(
  () => form.login_methods,
  (loginMethods) => {
    if (!loginMethods.includes(form.default_value)) {
      form.default_value = loginMethods[0] ?? ''
    }
  },
  { deep: true },
)

onMounted(loadSetting)
</script>

<template>
  <div v-loading="loading" class="flex h-full min-h-0 flex-col">
    <el-scrollbar class="min-h-0 flex-1">
      <el-form
        ref="authFormRef"
        class="max-w-200 px-6 pb-6 pt-4"
        :model="form"
        :rules="rules"
        label-position="top"
        require-asterisk-position="right"
      >
        <el-form-item label="允许的登录方式" prop="login_methods">
          <el-checkbox-group v-model="form.login_methods">
            <el-checkbox
              v-for="loginMethodOption in loginMethodOptions"
              :key="loginMethodOption.value"
              :value="loginMethodOption.value"
            >
              {{ loginMethodOption.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="默认登录方式" prop="default_value">
          <el-radio-group v-model="form.default_value">
            <el-radio
              v-for="loginMethodOption in selectedLoginMethodOptions"
              :key="loginMethodOption.value"
              :value="loginMethodOption.value"
            >
              {{ loginMethodOption.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="登录安全设置">
          <div class="space-y-3">
            <div class="flex items-center gap-2">
              <span>同一账号最多允许</span>
              <el-input-number
                v-model="form.max_attempts"
                :max="10"
                :min="-1"
                controls-position="right"
                @change="form.max_attempts = normalizeAttemptCount($event)"
              />
              <span>个会话同时登录</span>
              <span class="text-N500">（-1 表示不限制）</span>
            </div>
            <div class="flex items-center gap-2">
              <span>连续登录失败</span>
              <el-input-number
                v-model="form.failed_attempts"
                :max="10"
                :min="-1"
                controls-position="right"
                @change="form.failed_attempts = normalizeAttemptCount($event)"
              />
              <span>次后锁定</span>
              <el-input-number v-model="form.lock_time" :min="1" controls-position="right" />
              <span>分钟</span>
            </div>
          </div>
        </el-form-item>

        <el-button type="primary" @click="submit">保存</el-button>
      </el-form>
    </el-scrollbar>
  </div>
</template>
