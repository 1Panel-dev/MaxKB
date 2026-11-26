<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { QrLoginPlatformPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import ChatUserAuthScanApi from '@/api/admin/system/chat-management/chat-user-auth-scan'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { SCAN_FIELD_LABELS } from '@/constants'
import { copyText } from '@/utils/clipboard'
import { MsgError, MsgSuccess } from '@/utils/message'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive<QrLoginPlatformPayload>({ key: LOGIN_METHOD.WECOM, isActive: false, config: {} })

// 扫码登录回调地址沿用当前 API base 路径自动生成，只读展示。
const callbackUrl = computed(() => `${window.location.origin}${CHAT_API_BASE_PATH}/auth/${form.key}`)
const configKeys = computed(() => Object.keys(form.config).filter((key) => key !== 'callback_url'))

const rules = computed<FormRules>(() =>
  Object.fromEntries(
    configKeys.value.map((key) => [
      `config.${key}`,
      [
        {
          whitespace: true,
          required: true,
          message: t('common.validation.inputFieldRequired', { label: SCAN_FIELD_LABELS[key] ?? key }),
          trigger: 'blur',
        },
      ],
    ]),
  ),
)
function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    ChatUserAuthScanApi.postQrLoginPlatform(form)
      .then(() => {
        MsgSuccess(t('common.messages.saveSuccess'))
        emit('refresh')
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

/* 校验 */
function handleValidatePlatform() {
  loading.value = true
  return ChatUserAuthScanApi.putValidateQrLoginPlatform(form)
    .then((res) => {
      res ? MsgSuccess(t('auth.qrCode.messages.validationSuccess')) : MsgError(t('auth.qrCode.messages.validationFailed'))
    })
    .finally(() => {
      loading.value = false
    })
}

function open(platform: QrLoginPlatformPayload) {
  Object.assign(form, platform, { config: { ...platform.config } })
  form.config.callback_url = callbackUrl.value
  visible.value = true
}

function resetData() {
  Object.assign(form, { key: LOGIN_METHOD.WECOM, isActive: false, config: {} })
  formRef.value?.resetFields()
}
defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="t('common.configuration.title', { name: t(`auth.methods.${form.key}`) })" @closed="resetData">
    <el-form
      ref="formRef"
      v-loading="loading"
      :model="form"
      :rules="rules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item v-for="key in configKeys" :key="key" :label="SCAN_FIELD_LABELS[key] ?? key" :prop="`config.${key}`">
        <el-input
          v-model="form.config[key]"
          :autocomplete="key === 'app_secret' ? 'new-password' : 'off'"
          :show-password="key === 'app_secret'"
          :type="key === 'app_secret' ? 'password' : 'text'"
          :placeholder="t('common.placeholders.input')"
        />
      </el-form-item>
      <el-form-item :label="t('auth.fields.callbackUrl.label')">
        <el-input :model-value="callbackUrl" readonly>
          <template #suffix>
            <!-- 复制扫码登录回调地址 -->
            <el-button text class="-mr-1" :disabled="!callbackUrl" @click="copyText(callbackUrl)">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </template>
        </el-input>
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 校验 -->
      <el-button v-if="perm.system.chatAuth.edit()" plain @click="handleValidatePlatform">{{ t('auth.qrCode.validate') }}</el-button>
      <!-- 保存 -->
      <el-button v-if="perm.system.chatAuth.edit()" type="primary" @click="submit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDrawer>
</template>
