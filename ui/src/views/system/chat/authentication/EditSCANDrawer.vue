<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import ChatUserAuthScanApi from '@/api/admin/system/chat-user/chat-user-auth-scan'
import type { QrLoginPlatformPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { LOGIN_METHOD_LABELS, SCAN_FIELD_LABELS } from '@/constants'
import { LOGIN_METHOD } from '@/api/enums'
import { MsgSuccess, MsgError } from '@/utils/message'

const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive<QrLoginPlatformPayload>({ key: LOGIN_METHOD.WECOM, isActive: false, config: {} })

const rules = computed<FormRules>(() =>
  Object.fromEntries(Object.keys(form.config).map((key) => [`config.${key}`, [{ required: true, message: `请输入${SCAN_FIELD_LABELS[key] ?? key}`, trigger: 'blur' }]])),
)
function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    ChatUserAuthScanApi.postQrLoginPlatform(form)
      .then(() => {
        MsgSuccess('保存成功')
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
      res ? MsgSuccess('校验成功') : MsgError('校验失败')
    })
    .finally(() => {
      loading.value = false
    })
}

function open(platform: QrLoginPlatformPayload) {
  Object.assign(form, platform, { config: { ...platform.config } })
  visible.value = true
}

function resetData() {
  Object.assign(form, { key: LOGIN_METHOD.WECOM, isActive: false, config: {} })
  formRef.value?.resetFields()
}
defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="`${LOGIN_METHOD_LABELS[form.key]}设置`" @closed="resetData">
    <el-form ref="formRef" v-loading="loading" :model="form" :rules="rules" label-position="top" require-asterisk-position="right">
      <el-form-item v-for="(_, key) in form.config" :key="key" :label="SCAN_FIELD_LABELS[key] ?? key" :prop="`config.${key}`">
        <el-input v-model="form.config[key]" :show-password="key === 'app_secret'" :type="key === 'app_secret' ? 'password' : 'text'" placeholder="请输入" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button plain @click="handleValidatePlatform">校验</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDrawer>
</template>
