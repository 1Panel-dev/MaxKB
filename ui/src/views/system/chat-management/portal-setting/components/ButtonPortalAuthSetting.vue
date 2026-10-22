<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import type { PortalAuthConfig, PortalSetting, PortalSettingPayload } from '@/api/types'

const props = defineProps<{ disabled: boolean; setting: PortalSetting; saving: boolean; save: (payload: PortalSettingPayload) => Promise<void> }>()

/* 登录方式选项来自 system_options，默认登录方式仅允许选择草稿中已选的 login_value */
const loginMethodOptions = ref<NonNullable<PortalAuthConfig['system_options']>>([])
const defaultLoginMethodOptions = computed(() =>
  loginMethodOptions.value.filter(({ value }) => authForm.login_value.some((loginMethod) => loginMethod === value)),
)

const authVisible = ref(false)
const enableAuthAfterSave = ref(false)
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const authForm = reactive({
  login_value: [LOGIN_METHOD.LOCAL] as string[],
  type: LOGIN_METHOD.LOCAL as string,
  max_attempts: 1,
  failed_attempts: 5,
  lock_time: 10,
})

const authRules: FormRules<typeof authForm> = {
  login_value: [{ type: 'array', required: true, min: 1, message: '请选择至少一种登录方式', trigger: 'change' }],
  type: [{ required: true, message: '请选择默认登录方式', trigger: 'change' }],
}

/* 登录方式变化时，确保默认登录方式仍为已启用的方式 */
function handleLoginMethodsChange(loginMethods: string[]) {
  if (!loginMethods.includes(authForm.type)) {
    authForm.type = loginMethods[0] ?? ''
  }
}

/* 抽屉回填与重置，草稿不直接修改门户配置 */
function open(enableAfterSave = false) {
  if (props.disabled || props.saving) return

  enableAuthAfterSave.value = enableAfterSave
  const config = props.setting.auth_config ?? {}
  loginMethodOptions.value = config.system_options ?? []
  const loginMethods = [...(config.login_value?.length ? config.login_value : [LOGIN_METHOD.LOCAL])]
  const defaultType = config.type ?? LOGIN_METHOD.LOCAL
  const type = loginMethods.includes(defaultType) ? defaultType : (loginMethods[0] ?? LOGIN_METHOD.LOCAL)
  Object.assign(authForm, {
    login_value: loginMethods,
    type,
    max_attempts: config.max_attempts ?? 1,
    failed_attempts: config.failed_attempts ?? 5,
    lock_time: config.lock_time ?? 10,
  })
  authVisible.value = true
}

function handleOpenAuthSetting() {
  open()
}

function handleClosed() {
  enableAuthAfterSave.value = false
  Object.assign(authForm, {
    login_value: [LOGIN_METHOD.LOCAL],
    type: LOGIN_METHOD.LOCAL,
    max_attempts: 1,
    failed_attempts: 5,
    lock_time: 10,
  })
  authFormRef.value?.clearValidate()
}

/* 保存认证配置，仅提交表单字段 */
function handleSaveAuthSetting() {
  if (props.disabled || props.saving) return

  authFormRef.value?.validate((valid) => {
    if (!valid || props.disabled || props.saving) return
    return props
      .save({
        ...(enableAuthAfterSave.value ? { enable_auth: true } : {}),
        auth_config: {
          login_value: [...authForm.login_value],
          type: authForm.type,
          max_attempts: authForm.max_attempts,
          failed_attempts: authForm.failed_attempts,
          lock_time: authForm.lock_time,
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
      v-loading="saving"
      ref="authFormRef"
      :model="authForm"
      :rules="authRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="登录方式" prop="login_value">
        <el-checkbox-group v-model="authForm.login_value" @change="handleLoginMethodsChange" class="flex-wrap">
          <el-checkbox v-for="loginMethodOption in loginMethodOptions" :key="loginMethodOption.value" :value="loginMethodOption.value" class="w-32">
            {{ loginMethodOption.label }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="默认登录方式" prop="type">
        <el-select v-model="authForm.type">
          <el-option
            v-for="loginMethodOption in defaultLoginMethodOptions"
            :key="loginMethodOption.value"
            :value="loginMethodOption.value"
            :label="loginMethodOption.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="账号登录验证码设置" required>
        <div class="mk-gray-card-lg w-full space-y-4">
          <div class="flex-align-center gap-2">
            <span class="shrink-0">登录失败</span>
            <el-input-number v-model="authForm.max_attempts" class="w-32!" :min="-1" :max="100" :precision="0" :value-on-clear="1" />
            <span class="shrink-0">次显示验证码</span>
          </div>
          <div class="flex-align-center gap-2">
            <span class="shrink-0">登录失败</span>
            <el-input-number v-model="authForm.failed_attempts" class="w-32!" :min="1" :max="100" :precision="0" :value-on-clear="5" />
            <span class="shrink-0">次，锁定账号</span>
            <el-input-number v-model="authForm.lock_time" class="w-32!" :min="1" :max="1440" :precision="0" :value-on-clear="10" />
            <span class="shrink-0">分钟</span>
          </div>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消认证设置 -->
      <el-button plain :disabled="saving" @click="authVisible = false">取消</el-button>
      <!-- 保存认证设置 -->
      <el-button type="primary" :loading="saving" :disabled="saving" @click="handleSaveAuthSetting">保存</el-button>
    </template>
  </MkDrawer>
</template>
