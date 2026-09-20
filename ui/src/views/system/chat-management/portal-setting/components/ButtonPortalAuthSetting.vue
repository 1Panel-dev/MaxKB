<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { PortalSetting, PortalSettingPayload } from '@/api/types'
import { MsgError } from '@/utils/message'

const props = defineProps<{ setting: PortalSetting; saving: boolean; save: (payload: PortalSettingPayload) => Promise<void> }>()

/* 身份认证设置，仅修改已有后端消费的字段并保留其他配置 */
const authVisible = ref(false)
const enableAuthAfterSave = ref(false)
const authForm = reactive({ localLogin: true, maxAttempts: 1, failedAttempts: 5, lockTime: 10 })

function open(enableAfterSave = false) {
  handleClosed()
  enableAuthAfterSave.value = enableAfterSave
  const config = props.setting.auth_config
  Object.assign(authForm, {
    localLogin: config?.login_value?.includes('LOCAL') ?? true,
    maxAttempts: config?.max_attempts ?? 1,
    failedAttempts: config?.failed_attempts ?? 5,
    lockTime: config?.lock_time ?? 10,
  })
  authVisible.value = true
}

function handleSaveAuthSetting() {
  const config = props.setting.auth_config
  const loginMethods = (config.login_value || []).filter((method) => method !== 'LOCAL')
  if (authForm.localLogin) loginMethods.unshift('LOCAL')
  if (!loginMethods.length) {
    MsgError('请至少开启一种登录方式')
    return
  }
  return props
    .save({
      ...(enableAuthAfterSave.value ? { enable_auth: true } : {}),
      auth_config: {
        ...config,
        login_value: loginMethods,
        max_attempts: authForm.maxAttempts,
        failed_attempts: authForm.failedAttempts,
        lock_time: authForm.lockTime,
      },
    })
    .then(() => {
      authVisible.value = false
    })
}

function handleOpenAuthSetting() {
  open()
}

function handleClosed() {
  enableAuthAfterSave.value = false
  Object.assign(authForm, { localLogin: true, maxAttempts: 1, failedAttempts: 5, lockTime: 10 })
}

defineExpose({ open })
</script>

<template>
  <!-- 配置身份认证 -->
  <el-button text type="primary" title="身份认证设置" :disabled="saving" @click="handleOpenAuthSetting">
    <MkIcon name="icon-setting" />
  </el-button>
  <MkDialog v-model="authVisible" title="身份认证设置" :show-close="!saving" @closed="handleClosed">
    <el-form label-position="top" :disabled="saving" @submit.prevent>
      <el-form-item label="登录方式">
        <el-checkbox v-model="authForm.localLogin">本地账号登录</el-checkbox>
        <p class="w-full text-sm text-N600">使用对话用户账号登录门户。</p>
      </el-form-item>
      <el-form-item label="登录失败几次后显示验证码（0 为始终显示，-1 为不显示）">
        <el-input-number
          v-model="authForm.maxAttempts"
          :min="-1"
          :max="100"
          :precision="0"
          :value-on-clear="1"
          controls-position="right"
          align="left"
        />
      </el-form-item>
      <el-form-item label="连续登录失败次数上限">
        <el-input-number
          v-model="authForm.failedAttempts"
          :min="1"
          :max="100"
          :precision="0"
          :value-on-clear="5"
          controls-position="right"
          align="left"
        />
      </el-form-item>
      <el-form-item label="账号锁定时间（分钟）">
        <el-input-number
          v-model="authForm.lockTime"
          :min="1"
          :max="1440"
          :precision="0"
          :value-on-clear="10"
          controls-position="right"
          align="left"
        />
      </el-form-item>
      <p class="text-sm text-N600">失败次数与锁定时间的自定义配置在专业版、企业版生效。</p>
    </el-form>
    <template #footer>
      <!-- 取消认证设置 -->
      <el-button :disabled="saving" @click="authVisible = false">取消</el-button>
      <!-- 保存认证设置 -->
      <el-button type="primary" :loading="saving" @click="handleSaveAuthSetting">保存</el-button>
    </template>
  </MkDialog>
</template>
