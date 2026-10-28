<script setup lang="ts">
import { useApplicationDetailContext } from '../context'
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

import { APPLICATION_ACCESS_PLATFORM } from '@/api/enums'
import type { ApplicationAccessConfig } from '@/api/types'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import type { AccessPlatformDefinition } from './platforms'
import { isSystemResource } from '@/utils/resource-context.ts'
import perm from '@/permission/index.ts'

const { resourceApi } = useApplicationDetailContext()

defineOptions({ name: 'AccessSettingDrawer' })
const props = defineProps<{ applicationId: string; platform: AccessPlatformDefinition }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
const visible = ref(true)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive<ApplicationAccessConfig>({})

type ApplicationAccessPermissionMethod =
    | 'accessEdit'
function applicationAccessPermission(method: ApplicationAccessPermissionMethod): boolean {
  if (isSystemResource()) return Boolean(perm.application.system[method]())
  return Boolean(perm.application.workspace[method](props.applicationId))
}

const isWechat = computed(() => props.platform.key === APPLICATION_ACCESS_PLATFORM.WECHAT)
const modeField = computed(() => props.platform.modeField)
// 表单字段随连接方式切换：长连接(ws)需要 bot_id/secret，URL 回调(callback)需要 token/encoding_aes_key。
const activeFields = computed(() => {
  const mode = String(form[modeField.value?.key ?? ''] ?? modeField.value?.default ?? '')
  return (modeField.value && mode ? modeField.value.fields?.[mode] : undefined) ?? props.platform.fields
})
// 智能机器人默认长连接(ws)，无需回调地址；切到 URL 回调时才展示回调地址。
const showCallback = computed(() => !modeField.value || form[modeField.value.key] === 'callback')
// 消息回调沿用 Admin API 下的 /chat 路径，不使用独立 Chat 入口的 API base。
const callbackUrl = computed(() => `${window.location.origin}${ADMIN_API_BASE_PATH}/chat/${props.platform.key}/${props.applicationId}`)
const rules = computed<FormRules>(() =>
  Object.fromEntries(
    activeFields.value
      .filter((field) => field.required !== false)
      .map((field) => [field.key, [{ required: true, whitespace: true, message: `请输入 ${field.label}`, trigger: 'blur' }]]),
  ),
)

// 抽屉按需挂载，每次打开查询最新配置；未配置时使用空表单。
function loadPlatformConfig() {
  loading.value = true
  return resourceApi.access
    .getPlatformConfig(props.applicationId, props.platform.key)
    .then((config) => {
      Object.assign(form, config ?? {})
      if (modeField.value) form[modeField.value.key] = String(form[modeField.value.key] ?? modeField.value.default)
      activeFields.value.forEach((field) => {
        form[field.key] = String(form[field.key] ?? '')
      })
      if (isWechat.value) form.is_certification ??= false
    })
    .finally(() => {
      loading.value = false
    })
}

// 校验并保存当前平台，保留后端返回的其他配置字段。
function handleSave() {
  if (loading.value) return
  formRef.value?.validate((valid) => {
    if (!valid || loading.value) return
    loading.value = true
    const payload: ApplicationAccessConfig = { ...form, callback_url: callbackUrl.value }
    resourceApi.access
      .postPlatformConfig(props.applicationId, props.platform.key, payload)
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

onMounted(loadPlatformConfig)
</script>

<template>
  <MkDrawer v-model="visible" :title="`${platform.name}配置`" @closed="emit('closed')">
    <div v-loading="loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item v-if="modeField" label="连接方式" required>
          <!-- 选择发布渠道连接方式 -->
          <el-radio-group v-model="form[modeField.key]" class="w-full space-y-2">
            <template v-for="option in modeField.options" :key="option.value">
              <el-card shadow="hover" class="w-full" :class="{ 'border-primary!': form[modeField.key] === option.value }">
                <el-radio :value="option.value" class="mk-card-radio">
                  <h6>{{ option.label }}</h6>
                  <span class="block text-sm text-N600">{{ option.tip }}</span>
                </el-radio>
              </el-card>
            </template>
          </el-radio-group>
        </el-form-item>
        <template v-for="field in activeFields" :key="field.key">
          <el-form-item :label="field.label" :prop="field.key">
            <el-input
              v-model="form[field.key] as string"
              :type="field.secret ? 'password' : 'text'"
              :show-password="field.secret"
              :autocomplete="field.secret ? 'new-password' : 'off'"
              :placeholder="`请输入${field.label}`"
            />
          </el-form-item>
        </template>
        <el-form-item v-if="isWechat" label="认证成功">
          <!-- 设置公众号认证状态 -->
          <el-switch v-model="form.is_certification" />
        </el-form-item>

        <el-form-item v-if="showCallback" label="回调地址">
          <el-input :model-value="callbackUrl" readonly>
            <template #suffix>
              <!-- 复制发布渠道回调地址 -->
              <el-button text class="-mr-1" :disabled="!callbackUrl" @click="copyText(callbackUrl)">
                <MkIcon name="icon_copy_outlined" />
              </el-button>
            </template>
          </el-input>

          <p v-if="platform.consoleUrl" class="mt-2 text-N500">
            复制链接填入到
            <!-- 打开对应平台后台配置回调 -->
            <a class="mk-link" :href="platform.consoleUrl" target="_blank">
              {{ platform.consoleName }}
            </a>
            {{ platform.callbackTip }}
          </p>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <!-- 取消发布渠道配置 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存发布渠道配置 -->
      <el-button v-if="applicationAccessPermission('accessEdit')" type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </MkDrawer>
</template>
