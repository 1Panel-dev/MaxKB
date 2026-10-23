<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApiKeyPayload, ApiKeyRecord } from '@/api/types'
import type ApplicationApiKeyApi from '@/api/admin/workspace/application/api-key'
import type SystemResourceApiKeyApi from '@/api/admin/system/resource-management/application/api-key'
import type SystemApiKeyApi from '@/api/admin/system/api-key'
import { expirationOptions, getApiKeyExpireTime, type ExpirationType } from '../expiration'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ButtonEditApiKey' })

const props = defineProps<{
  api: typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi | typeof SystemApiKeyApi
  applicationId?: string
  record: ApiKeyRecord
}>()
const emit = defineEmits<{ refresh: [] }>()
/* 编辑 API Key 与配置抽屉 */
const visible = ref(false)
const saving = ref(false)
const apiKeyId = ref('')
const formRef = useTemplateRef<FormInstance>('formRef')

interface ApiKeyForm {
  secret_key: string
  expirationType: ExpirationType
  expire_time: string | null
  remark: string
  allow_cross_domain: boolean
  cross_domain_list: string
  is_active: boolean
}

const form = reactive<ApiKeyForm>({
  secret_key: '',
  expirationType: 'never',
  expire_time: null,
  remark: '',
  allow_cross_domain: false,
  cross_domain_list: '',
  is_active: true,
})

const rules: FormRules<ApiKeyForm> = {
  expirationType: [{ required: true, message: '请选择到期时间', trigger: 'change' }],
  expire_time: [
    {
      validator: (_rule, value: string | null, callback) => {
        if (form.expirationType !== 'custom') return callback()
        const timestamp = value ? new Date(value).getTime() : NaN
        if (!Number.isFinite(timestamp) || timestamp <= Date.now()) return callback(new Error('请选择晚于当前时间的到期时间'))
        callback()
      },
      trigger: 'change',
    },
  ],
}

function handleOpenEdit() {
  const record = props.record
  apiKeyId.value = record.id
  Object.assign(form, {
    secret_key: record.secret_key,
    expirationType: record.is_permanent ? 'never' : 'custom',
    expire_time: record.expire_time,
    remark: record.remark ?? '',
    allow_cross_domain: record.allow_cross_domain,
    cross_domain_list: record.cross_domain_list.join('\n'),
    is_active: record.is_active,
  })
  visible.value = true
}

function handleExpirationChange() {
  form.expire_time = null
  formRef.value?.clearValidate('expire_time')
}

function handleSave() {
  if (saving.value) return
  return formRef.value?.validate((valid) => {
    if (!valid || saving.value) return
    const payload: ApiKeyPayload = {
      is_permanent: form.expirationType === 'never',
      expire_time: getApiKeyExpireTime(form.expirationType, form.expire_time),
      remark: form.remark,
      allow_cross_domain: form.allow_cross_domain,
      cross_domain_list: form.cross_domain_list
        .split('\n')
        .map((address) => address.trim())
        .filter(Boolean),
      is_active: form.is_active,
    }
    saving.value = true
    const request =
      props.applicationId !== undefined
        ? (props.api as typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi).putApiKey(props.applicationId, apiKeyId.value, payload)
        : (props.api as typeof SystemApiKeyApi).putApiKey(apiKeyId.value, payload)
    return request
      .then(() => {
        MsgSuccess('保存成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        saving.value = false
      })
  })
}

function handleClosed() {
  apiKeyId.value = ''
  form.secret_key = ''
  form.expirationType = 'never'
  form.expire_time = null
  form.remark = ''
  form.allow_cross_domain = false
  form.cross_domain_list = ''
  form.is_active = true
  formRef.value?.clearValidate()
}
</script>

<template>
  <!-- 编辑 API Key -->
  <MkTooltip content="编辑" placement="top">
    <el-button type="primary" text @click.stop="handleOpenEdit">
      <MkIcon name="icon_edit_outlined" />
    </el-button>
  </MkTooltip>
  <MkDrawer v-model="visible" title="编辑 API Key" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" :inert="saving" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="API KEY">
        <el-input :model-value="form.secret_key" disabled>
          <template #suffix>
            <!-- 复制 API Key -->
            <el-button text @click="copyText(form.secret_key)" class="-mr-1">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="到期时间" prop="expirationType">
        <el-select v-model="form.expirationType" @change="handleExpirationChange">
          <template v-for="option in expirationOptions" :key="option.value">
            <el-option :label="option.label" :value="option.value" />
          </template>
        </el-select>
      </el-form-item>
      <el-form-item v-if="form.expirationType === 'custom'" prop="expire_time">
        <el-date-picker v-model="form.expire_time" class="w-full!" type="datetime" value-format="YYYY-MM-DDTHH:mm:ssZ" placeholder="请选择到期时间" />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <!-- TODO：后端支持 remark 后移除联调提示。 -->
        <el-input v-model="form.remark" type="textarea" :rows="3" maxlength="256" show-word-limit placeholder="请输入" />
      </el-form-item>
      <el-form-item label="跨域设置">
        <el-switch v-model="form.allow_cross_domain" />
      </el-form-item>
      <el-form-item v-if="form.allow_cross_domain">
        <el-input
          v-model="form.cross_domain_list"
          type="textarea"
          :rows="8"
          :placeholder="'请输入允许的跨域地址，开启后不输入跨域地址则不限制。\n跨域地址一行一个，如：\nhttp://127.0.0.1:5678\nhttps://dataease.io'"
        />
      </el-form-item>
      <el-form-item label="启用状态">
        <el-switch v-model="form.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消编辑 -->
      <el-button plain :disabled="saving" @click="visible = false">取消</el-button>
      <!-- 保存 API Key 配置 -->
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </template>
  </MkDrawer>
</template>
