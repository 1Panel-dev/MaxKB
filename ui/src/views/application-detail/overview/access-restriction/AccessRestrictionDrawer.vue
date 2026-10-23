<script setup lang="ts">
import { onMounted, reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ApplicationAuthenticationConfig, ApplicationAccessTokenPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import { useApplicationDetailContext } from '../../context'

defineOptions({ name: 'AccessRestrictionDrawer' })

const emit = defineEmits<{ closed: [] }>()
const { applicationId, resourceApi } = useApplicationDetailContext()
const visible = ref(true)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive({
  language: undefined as string | undefined,
  authentication_value: {} as ApplicationAuthenticationConfig,
  access_num: 100,
  authentication: false,
  white_active: false,
  white_list: '',
})

function loadAccessRestriction() {
  if (loading.value) return
  loading.value = true
  return resourceApi.application
    .getAccessToken(applicationId.value)
    .then((config) => {
      Object.assign(form, {
        language: config.language,
        authentication_value: cloneDeep(config.authentication_value ?? {}),
        access_num: config.access_num,
        authentication: config.authentication ?? false,
        white_active: config.white_active,
        white_list: config.white_list?.join('\n') ?? '',
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSave() {
  if (loading.value) return
  formRef.value?.validate((valid) => {
    if (!valid || loading.value) return
    const payload: ApplicationAccessTokenPayload = {
      access_num: form.access_num,
      white_active: form.white_active,
      white_list: form.white_list
        .split('\n')
        .map((origin) => origin.trim())
        .filter(Boolean),
      // 后端省略 language 会清空配置，访问限制保存时保留原值。
      language: form.language,
      authentication: form.authentication,
      authentication_value: cloneDeep(form.authentication_value),
    }
    loading.value = true
    return resourceApi.application
      .putAccessToken(applicationId.value, payload)
      .then(() => {
        MsgSuccess('保存成功')
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

onMounted(loadAccessRestriction)
</script>

<template>
  <MkDrawer v-model="visible" title="访问限制" @closed="emit('closed')">
    <div v-loading="loading">
      <el-form ref="formRef" :model="form" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item label="每个客户端提问限制">
          <el-input-number
            v-model="form.access_num"
            class="w-32!"
            :min="0"
            :max="10000000"
            :step="1"
            :value-on-clear="0"
            step-strictly
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
        <el-form-item label="嵌入白名单">
          <div class="w-full space-y-2">
            <!-- 设置嵌入白名单 -->
            <el-switch v-model="form.white_active" />
            <el-input
              v-if="form.white_active"
              v-model="form.white_list"
              type="textarea"
              :rows="8"
              :placeholder="'请输入允许嵌入第三方的源地址，一行一个，如：\nhttp://127.0.0.1:5678\nhttps://dataease.io'"
            />
          </div>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <!-- 取消访问限制设置 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存访问限制设置 -->
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </MkDrawer>
</template>
