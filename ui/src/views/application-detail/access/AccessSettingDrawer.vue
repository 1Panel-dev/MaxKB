<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import AccessApi from '@/api/admin/workspace/application/access'
import { APPLICATION_ACCESS_PLATFORM } from '@/api/enums'
import type { ApplicationAccessConfig, Dict } from '@/api/types'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import type { AccessPlatformDefinition } from './platforms'

defineOptions({ name: 'AccessSettingDrawer' })
const props = defineProps<{ applicationId: string; platform: AccessPlatformDefinition }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
const visible = ref(true)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive<Dict<string>>({})
const isCertification = ref(false)
let savedConfig: ApplicationAccessConfig = {}

const isWechat = computed(() => props.platform.key === APPLICATION_ACCESS_PLATFORM.WECHAT)
const modeField = computed(() => props.platform.modeField)
// 表单字段随连接方式切换：长连接(ws)需要 bot_id/secret，URL 回调(callback)需要 token/encoding_aes_key。
const activeFields = computed(() => {
  const mode = form[modeField.value?.key ?? ''] ?? modeField.value?.default
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
  return AccessApi.getPlatformConfig(props.applicationId, props.platform.key)
    .then((config) => {
      savedConfig = config ?? {}
      if (modeField.value) form[modeField.value.key] = String(savedConfig[modeField.value.key] ?? modeField.value.default)
      activeFields.value.forEach((field) => {
        form[field.key] = String(savedConfig[field.key] ?? '')
      })
      isCertification.value = savedConfig.is_certification ?? false
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
    const payload: ApplicationAccessConfig = { ...savedConfig, ...form, callback_url: callbackUrl.value }
    if (isWechat.value) payload.is_certification = isCertification.value
    AccessApi.postPlatformConfig(props.applicationId, props.platform.key, payload)
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
    <div v-loading="loading" class="min-h-40">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item v-if="modeField" label="连接方式" required>
          <div class="w-full space-y-4">
            <div
              v-for="option in modeField.options"
              :key="option.value"
              class="flex min-h-[74px] w-full cursor-pointer items-center justify-between rounded-xl border px-4 py-3"
              :class="form[modeField.key] === option.value ? 'border-primary!' : 'border-N200'"
              @click="form[modeField.key] = option.value"
            >
              <div class="flex min-w-0 flex-col">
                <span class="text-N900">{{ option.label }}</span>
                <span class="mt-0.5 text-N500">{{ option.tip }}</span>
              </div>
              <span
                class="ml-4 flex size-4 shrink-0 items-center justify-center rounded-full border"
                :class="form[modeField.key] === option.value ? 'border-primary' : 'border-N300'"
              >
                <span v-if="form[modeField.key] === option.value" class="size-2 rounded-full bg-primary" />
              </span>
            </div>
          </div>
        </el-form-item>
        <template v-for="field in activeFields" :key="field.key">
          <el-form-item :label="field.label" :prop="field.key">
            <el-input
              v-model="form[field.key]"
              :type="field.secret ? 'password' : 'text'"
              :show-password="field.secret"
              :autocomplete="field.secret ? 'new-password' : 'off'"
              :placeholder="`请输入${field.label}`"
            />
          </el-form-item>
        </template>
        <el-form-item v-if="isWechat" label="认证成功">
          <!-- 设置公众号认证状态 -->
          <el-switch v-model="isCertification" />
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
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </MkDrawer>
</template>
