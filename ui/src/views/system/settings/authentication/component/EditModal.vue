<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import PlatformSourceApi from '@/api/admin/system/platform-source'
import type { QrLoginPlatformRequest, QrLoginPlatformType } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

interface QrLoginPlatformEditorData extends QrLoginPlatformRequest {
  name: string
}

const emit = defineEmits<{ saved: [] }>()
const visible = ref(false)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive<QrLoginPlatformEditorData>({
  key: 'wecom',
  name: '',
  isActive: false,
  config: {},
})
const fieldLabels: Record<string, string> = {
  agent_id: 'Agent ID',
  app_key: 'App Key',
  app_secret: 'App Secret',
  callback_url: '回调地址',
  corp_id: 'Corp ID',
}
const rules = computed<FormRules>(() =>
  Object.fromEntries(
    Object.keys(form.config).map((key) => [
      `config.${key}`,
      [{ required: true, message: `请输入${fieldLabels[key] ?? key}`, trigger: 'blur' }],
    ]),
  ),
)

function resetData() {
  Object.assign(form, { key: 'wecom', name: '', isActive: false, config: {} })
  formRef.value?.resetFields()
}

function open(platform: QrLoginPlatformEditorData) {
  resetData()
  Object.assign(form, platform, { config: { ...platform.config } })
  visible.value = true
}

function close() {
  visible.value = false
  resetData()
}

function createRequest(): QrLoginPlatformRequest {
  return { key: form.key as QrLoginPlatformType, isActive: form.isActive, config: form.config }
}

function submit(action: 'save' | 'test') {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    const request =
      action === 'test'
        ? PlatformSourceApi.postQrLoginPlatformConnection(createRequest())
        : PlatformSourceApi.putQrLoginPlatform(createRequest())

    request
      .then(() => {
        MsgSuccess(action === 'test' ? '验证成功' : '保存成功')
        if (action === 'save') {
          emit('saved')
          close()
        }
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="`${form.name}设置`" size="560" @closed="resetData">
    <el-form
      ref="formRef"
      v-loading="loading"
      :model="form"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item
        v-for="(_, key) in form.config"
        :key="key"
        :label="fieldLabels[key] ?? key"
        :prop="`config.${key}`"
      >
        <el-input
          v-model="form.config[key]"
          :show-password="key === 'app_secret'"
          :type="key === 'app_secret' ? 'password' : 'text'"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button @click="submit('test')">验证</el-button>
      <el-button type="primary" @click="submit('save')">保存</el-button>
    </template>
  </MkDrawer>
</template>
