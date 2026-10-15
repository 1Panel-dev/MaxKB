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
// 消息回调沿用 Admin API 下的 /chat 路径，不使用独立 Chat 入口的 API base。
const callbackUrl = computed(() => `${window.location.origin}${ADMIN_API_BASE_PATH}/chat/${props.platform.key}/${props.applicationId}`)
const rules = computed<FormRules>(() =>
  Object.fromEntries(
    props.platform.fields
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
      props.platform.fields.forEach((field) => {
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
        <template v-for="field in platform.fields" :key="field.key">
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

        <el-form-item label="回调地址">
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
