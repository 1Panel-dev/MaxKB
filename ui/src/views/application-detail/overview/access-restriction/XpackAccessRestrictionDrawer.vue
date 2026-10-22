<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserAuthApi from '@/api/admin/system/chat-management/chat-user-auth'
import { LOGIN_METHOD } from '@/api/enums'
import type { ApplicationAccessToken, ApplicationAccessTokenPayload, LoginMethod, OptionItem } from '@/api/types'
import { LOGIN_METHOD_LABELS } from '@/constants/auth'
import { MsgSuccess } from '@/utils/message'
import { useApplicationDetailContext } from '../../context'

defineOptions({ name: 'XpackAccessRestrictionDrawer' })

const emit = defineEmits<{ closed: [] }>()
const { applicationId, resourceApi } = useApplicationDetailContext()
const visible = ref(true)
const loading = ref(false)
const saving = ref(false)
const savedConfig = ref<ApplicationAccessToken>()
const loginMethodOptions = ref<OptionItem<string>[]>([])
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive({
  access_num: 100,
  authentication: false,
  login_value: [] as string[],
  default_value: '',
  max_attempts: 1,
  failed_attempts: 5,
  lock_time: 10,
  white_active: false,
  white_list: '',
})

const defaultLoginMethodOptions = computed(() => loginMethodOptions.value.filter((option) => form.login_value.includes(option.value)))
const rules: FormRules<typeof form> = {
  access_num: [{ required: true, type: 'integer', min: 0, max: 10000000, message: '请输入 0～10000000 的整数', trigger: 'change' }],
  login_value: [{ required: true, type: 'array', min: 1, message: '请选择至少一种登录方式', trigger: 'change' }],
  default_value: [{ required: true, message: '请选择默认登录方式', trigger: 'change' }],
  max_attempts: [{ required: true, type: 'integer', min: -1, max: 10, message: '请输入 -1～10 的整数', trigger: 'change' }],
  failed_attempts: [{ required: true, type: 'integer', min: 1, max: 100, message: '请输入 1～100 的整数', trigger: 'change' }],
  lock_time: [{ required: true, type: 'integer', min: 1, max: 1440, message: '请输入 1～1440 的整数', trigger: 'change' }],
}

function handleLoginMethodsChange() {
  if (!form.login_value.includes(form.default_value)) {
    form.default_value = form.login_value[0] ?? ''
  }
}

// 每次挂载读取当前范围配置；登录方式加载成功后再允许保存。
function loadAccessRestriction() {
  if (loading.value) return
  loading.value = true
  return resourceApi.application
    .getAccessToken(applicationId.value)
    .then((config) => {
      const authConfig = config.authentication_value
      return ChatUserAuthApi.getChatUserAuthType().then((options) => {
        loginMethodOptions.value = options
        Object.assign(form, {
          access_num: config.access_num,
          authentication: config.authentication ?? false,
          login_value: [...(authConfig?.login_value ?? (options.some((option) => option.value === LOGIN_METHOD.LOCAL) ? [LOGIN_METHOD.LOCAL] : []))],
          default_value: authConfig?.default_value ?? '',
          max_attempts: authConfig?.max_attempts ?? 1,
          failed_attempts: authConfig?.failed_attempts ?? 5,
          lock_time: authConfig?.lock_time ?? 10,
          white_active: config.white_active,
          white_list: config.white_list?.join('\n') ?? '',
        })
        handleLoginMethodsChange()
        savedConfig.value = config
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSave() {
  if (!savedConfig.value || loading.value || saving.value) return
  formRef.value?.validate((valid) => {
    if (!valid || !savedConfig.value || loading.value || saving.value) return
    const payload: ApplicationAccessTokenPayload = {
      access_num: form.access_num,
      white_active: form.white_active,
      white_list: form.white_list
        .split('\n')
        .map((origin) => origin.trim())
        .filter(Boolean),
      // 后端省略 language 会清空配置，访问限制保存时保留原值。
      language: savedConfig.value.language,
      authentication: form.authentication,
      authentication_value: {
        ...cloneDeep(savedConfig.value.authentication_value ?? {}),
        type: savedConfig.value.authentication_value?.type ?? 'login',
        login_value: [...form.login_value],
        default_value: form.default_value,
        max_attempts: form.max_attempts,
        failed_attempts: form.failed_attempts,
        lock_time: form.lock_time,
      },
    }
    saving.value = true
    return resourceApi.application
      .putAccessToken(applicationId.value, payload)
      .then(() => {
        MsgSuccess('保存成功')
        visible.value = false
      })
      .finally(() => {
        saving.value = false
      })
  })
}

onMounted(loadAccessRestriction)
</script>

<template>
  <MkDrawer v-model="visible" title="访问限制" size="600" content-class="h-full" @closed="emit('closed')">
    <div v-loading="loading" class="h-full" :inert="saving">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item label="每个客户端提问限制" prop="access_num">
          <el-input-number
            v-model="form.access_num"
            class="w-32!"
            :min="0"
            :max="10000000"
            :precision="0"
            :value-on-clear="100"
            controls-position="right"
            align="left"
          />
          <span class="ml-2">次/天</span>
        </el-form-item>
        <el-form-item>
          <template #label>
            <span class="flex-align-center gap-1">
              身份认证
              <MkTooltip content="开启身份认证后，智能体和关联的知识库均需要对话用户授权配置，否则用户无权限登录和知识库检索">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </span>
          </template>
          <!-- 设置身份认证 -->
          <el-switch v-model="form.authentication" />
        </el-form-item>
        <template v-if="form.authentication">
          <el-form-item label="登录方式" prop="login_value">
            <!-- 选择允许的登录方式 -->
            <el-checkbox-group v-model="form.login_value" class="flex-wrap gap-x-6" @change="handleLoginMethodsChange">
              <template v-for="option in loginMethodOptions" :key="option.value">
                <el-checkbox :value="option.value" :disabled="option.disabled" class="w-32">
                  {{ LOGIN_METHOD_LABELS[option.value as LoginMethod] || option.label }}
                </el-checkbox>
              </template>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="默认登录方式" prop="default_value">
            <el-select v-model="form.default_value" placeholder="请选择默认登录方式">
              <template v-for="option in defaultLoginMethodOptions" :key="option.value">
                <el-option :value="option.value" :label="LOGIN_METHOD_LABELS[option.value as LoginMethod] || option.label" />
              </template>
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.login_value.includes(LOGIN_METHOD.LOCAL)" label="账号登录验证码设置" required>
            <div class="mk-gray-card-lg w-full space-y-4">
              <div class="flex-align-center gap-2">
                <span class="shrink-0">登录失败</span>
                <el-form-item prop="max_attempts" class="mb-0!">
                  <el-input-number v-model="form.max_attempts" class="w-32!" :min="-1" :max="10" :precision="0" :value-on-clear="1" />
                </el-form-item>
                <span class="shrink-0">次显示验证码</span>
              </div>
              <div class="flex-align-center gap-2">
                <span class="shrink-0">登录失败</span>
                <el-form-item prop="failed_attempts" class="mb-0!">
                  <el-input-number v-model="form.failed_attempts" class="w-32!" :min="1" :max="100" :precision="0" :value-on-clear="5" />
                </el-form-item>
                <span class="shrink-0">次，锁定账号</span>
                <el-form-item prop="lock_time" class="mb-0!">
                  <el-input-number v-model="form.lock_time" class="w-32!" :min="1" :max="1440" :precision="0" :value-on-clear="10" />
                </el-form-item>
                <span class="shrink-0">分钟</span>
              </div>
            </div>
          </el-form-item>
        </template>
        <el-form-item label="嵌入白名单">
          <div class="w-full space-y-2">
            <!-- 设置嵌入白名单 -->
            <el-switch v-model="form.white_active" />
            <el-input
              v-if="form.white_active"
              v-model="form.white_list"
              type="textarea"
              :rows="8"
              placeholder="请输入允许嵌入第三方的源地址，一行一个，如：&#10;http://127.0.0.1:5678&#10;https://dataease.io"
            />
          </div>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <!-- 取消访问限制设置 -->
      <el-button plain :disabled="saving" @click="visible = false">取消</el-button>
      <!-- 保存访问限制设置 -->
      <el-button type="primary" :loading="saving" :disabled="loading" @click="handleSave">保存</el-button>
    </template>
  </MkDrawer>
</template>
