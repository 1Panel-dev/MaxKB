<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import AuthSettingApi from '@/api/admin/system/settings/auth-setting'
import type { LoginMethod, PortalSetting, PortalSettingPayload } from '@/api/types'
import { LOGIN_METHOD_LABELS } from '@/constants/auth'

const props = defineProps<{ disabled: boolean; setting: PortalSetting; saving: boolean; save: (payload: PortalSettingPayload) => Promise<void> }>()

/* 登录方式与默认登录方式 */
const loginMethodOptions = ref<string[]>([LOGIN_METHOD.LOCAL])
const loginMethodsLoading = ref(false)

function loadLoginMethodOptions() {
  loginMethodsLoading.value = true
  return AuthSettingApi.getLoginSetting()
    .then((setting) => {
      loginMethodOptions.value = setting.login_methods ?? [LOGIN_METHOD.LOCAL]
    })
    .finally(() => {
      loginMethodsLoading.value = false
    })
}
const authVisible = ref(false)
const enableAuthAfterSave = ref(false)
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const authForm = reactive({
  loginMethods: [LOGIN_METHOD.LOCAL] as string[],
  maxAttempts: 1,
  failedAttempts: 5,
  lockTime: 10,
})
const authRules: FormRules<typeof authForm> = {
  loginMethods: [{ type: 'array', required: true, min: 1, message: '请选择至少一种登录方式', trigger: 'change' }],
}

/* 抽屉回填与重置，草稿不直接修改门户配置 */
function open(enableAfterSave = false) {
  if (props.disabled || props.saving) return

  enableAuthAfterSave.value = enableAfterSave
  const config = props.setting.auth_config
  Object.assign(authForm, {
    loginMethods: [...(config.login_value ?? [LOGIN_METHOD.LOCAL])],
    maxAttempts: config.max_attempts ?? 1,
    failedAttempts: config.failed_attempts ?? 5,
    lockTime: config.lock_time ?? 10,
  })
  authVisible.value = true
  loadLoginMethodOptions()
}

function handleOpenAuthSetting() {
  open()
}

function handleClosed() {
  enableAuthAfterSave.value = false
  Object.assign(authForm, {
    loginMethods: [LOGIN_METHOD.LOCAL],
    maxAttempts: 1,
    failedAttempts: 5,
    lockTime: 10,
  })
  authFormRef.value?.clearValidate()
}

/* 保存认证配置，仅提交后端读取的字段并保留其余配置 */
function handleSaveAuthSetting() {
  if (props.disabled || props.saving || loginMethodsLoading.value) return

  authFormRef.value?.validate((valid) => {
    if (!valid || props.disabled || props.saving || loginMethodsLoading.value) return
    return props
      .save({
        ...(enableAuthAfterSave.value ? { enable_auth: true } : {}),
        auth_config: {
          ...props.setting.auth_config,
          login_value: [...authForm.loginMethods],
          max_attempts: authForm.maxAttempts,
          failed_attempts: authForm.failedAttempts,
          lock_time: authForm.lockTime,
        },
      })
      .then(() => {
        authVisible.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <!-- 配置身份认证 -->
  <el-button text type="primary" title="身份认证设置" :disabled="disabled || saving" @click="handleOpenAuthSetting">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDrawer v-model="authVisible" title="身份认证设置" @closed="handleClosed">
    <el-form
      v-loading="loginMethodsLoading || saving"
      ref="authFormRef"
      :model="authForm"
      :rules="authRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="登录方式" prop="loginMethods">
        <el-checkbox-group v-model="authForm.loginMethods" class="flex-wrap">
          <template v-for="loginMethod in loginMethodOptions" :key="loginMethod">
            <el-checkbox :value="loginMethod" class="w-32">{{ LOGIN_METHOD_LABELS[loginMethod as LoginMethod] || loginMethod }}</el-checkbox>
          </template>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="账号登录验证码设置" required>
        <div class="mk-gray-card-lg w-full space-y-4">
          <div class="flex-align-center gap-2">
            <span class="shrink-0">登录失败</span>
            <el-input-number v-model="authForm.maxAttempts" class="w-32!" :min="-1" :max="100" :precision="0" :value-on-clear="1" />
            <span class="shrink-0">次显示验证码</span>
          </div>
          <div class="flex-align-center gap-2">
            <span class="shrink-0">登录失败</span>
            <el-input-number v-model="authForm.failedAttempts" class="w-32!" :min="1" :max="100" :precision="0" :value-on-clear="5" />
            <span class="shrink-0">次，锁定账号</span>
            <el-input-number v-model="authForm.lockTime" class="w-32!" :min="1" :max="1440" :precision="0" :value-on-clear="10" />
            <span class="shrink-0">分钟</span>
          </div>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消认证设置 -->
      <el-button plain :disabled="saving" @click="authVisible = false">取消</el-button>
      <!-- 保存认证设置 -->
      <el-button type="primary" :loading="saving" :disabled="loginMethodsLoading" @click="handleSaveAuthSetting">保存</el-button>
    </template>
  </MkDrawer>
</template>
