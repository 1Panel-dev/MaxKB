<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import AuthSettingApi from '@/api/admin/system/auth-setting'
import type { AuthProviderSetting, AuthProviderType } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

export interface AuthProviderField {
  defaultValue?: string | boolean
  key: string
  label: string
  placeholder?: string
  required?: boolean
  rows?: number
  type?: 'password' | 'textarea' | 'switch'
}

const props = withDefaults(
  defineProps<{
    authType: AuthProviderType
    fields: AuthProviderField[]
    testable?: boolean
  }>(),
  { testable: false },
)

const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<AuthProviderSetting>(createDefaultSetting())
const rules = computed<FormRules>(() =>
  Object.fromEntries(
    props.fields
      .filter(({ required = true, type }) => required && type !== 'switch')
      .map(({ key, label }) => [
        `config.${key}`,
        [{ required: true, message: `请输入${label}`, trigger: 'blur' }],
      ]),
  ),
)

function createDefaultSetting(): AuthProviderSetting {
  return {
    auth_type: props.authType,
    config: Object.fromEntries(
      props.fields.map(({ defaultValue = '', key }) => [key, defaultValue]),
    ),
    is_active: false,
  }
}

/* 认证源配置加载与提交 */
function loadSetting() {
  loading.value = true
  return AuthSettingApi.getAuthSetting(props.authType)
    .then((setting) => {
      const defaultSetting = createDefaultSetting()
      Object.assign(form, defaultSetting, setting, {
        config: { ...defaultSetting.config, ...setting.config },
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function submit(action: 'save' | 'test') {
  authFormRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    const request =
      action === 'test'
        ? AuthSettingApi.postAuthSettingConnection(form)
        : AuthSettingApi.putAuthSetting(props.authType, form)

    request
      .then(() => MsgSuccess(action === 'test' ? '连接成功' : '保存成功'))
      .finally(() => {
        loading.value = false
      })
  })
}

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
        <template v-for="field in fields" :key="field.key">
          <el-form-item v-if="field.type === 'switch'">
            <div class="flex flex-col">
              <span>{{ field.label }}</span>
              <el-switch v-model="form.config[field.key]" class="self-start" />
            </div>
          </el-form-item>
          <el-form-item v-else :label="field.label" :prop="`config.${field.key}`">
            <el-input
              v-model="form.config[field.key]"
              :placeholder="field.placeholder || `请输入${field.label}`"
              :rows="field.rows ?? (field.type === 'textarea' ? 4 : undefined)"
              :show-password="field.type === 'password'"
              :type="field.type ?? 'text'"
            />
          </el-form-item>
        </template>

        <el-form-item>
          <div class="flex flex-col">
            <span>启用认证</span>
            <el-switch v-model="form.is_active" class="self-start" />
          </div>
        </el-form-item>

        <div class="flex gap-3">
          <el-button type="primary" @click="submit('save')">保存</el-button>
          <el-button v-if="testable" @click="submit('test')">测试连接</el-button>
        </div>
      </el-form>
    </el-scrollbar>
  </div>
</template>
