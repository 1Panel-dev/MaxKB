<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatUserQuotaPayload, PeriodType, QuotaType } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { PERIOD_TYPE, QUOTA_TYPE } from '@/api/enums'
import ChatUserApi from '@/api/admin/system/chat-management/chat-user'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'QuotaSettingsDialog' })

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ refresh: [] }>()

interface QuotaSettingsForm {
  periodType: PeriodType
  periodValue: number
  quotaType: QuotaType
  tokenLimit: number
}

const periodTypeOptions = computed<Array<{ label: string; value: PeriodType }>>(() => [
  { label: t('common.schedule.units.days', quotaSettingsForm.periodValue), value: PERIOD_TYPE.DAY },
  { label: t('common.schedule.units.weeks', quotaSettingsForm.periodValue), value: PERIOD_TYPE.WEEK },
  { label: t('common.schedule.units.months', quotaSettingsForm.periodValue), value: PERIOD_TYPE.MONTH },
])

const dialogVisible = ref(false)
const quotaSettingsFormRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const pendingUserIds = ref<string[]>([])

const quotaSettingsForm = reactive<QuotaSettingsForm>({
  periodType: PERIOD_TYPE.MONTH,
  periodValue: 1,
  quotaType: QUOTA_TYPE.UNLIMITED,
  tokenLimit: 10_000_000,
})
const quotaSettingsRules = computed<FormRules<QuotaSettingsForm>>(() => ({
  periodValue: [{ required: true, message: t('chatUser.quota.period.requiredMessage'), trigger: 'change' }],
  tokenLimit: [{ required: true, message: t('chatUser.quota.tokenLimit.requiredMessage'), trigger: 'change' }],
}))

function buildPayload(): ChatUserQuotaPayload {
  if (quotaSettingsForm.quotaType === QUOTA_TYPE.UNLIMITED) {
    return { quota_type: QUOTA_TYPE.UNLIMITED, period_type: null, period_value: null, token_limit: null }
  }
  return {
    quota_type: QUOTA_TYPE.PERIODIC,
    period_type: quotaSettingsForm.periodType,
    period_value: quotaSettingsForm.periodValue,
    // 前端单位是 K，传给后端时为原始 token 数
    token_limit: quotaSettingsForm.tokenLimit * 1000,
  }
}

function submitQuotaSettings() {
  quotaSettingsFormRef.value?.validate((valid) => {
    if (!valid) return

    submitting.value = true
    const payload = buildPayload()
    const request =
      pendingUserIds.value.length === 1
        ? ChatUserApi.postChatUserQuota(pendingUserIds.value[0]!, payload)
        : ChatUserApi.postBatchSetChatUserQuota({ ...payload, user_ids: pendingUserIds.value })

    request
      .then(() => {
        MsgSuccess(t('chatUser.quota.saveSuccess'))
        emit('refresh')
        dialogVisible.value = false
      })
      .finally(() => {
        submitting.value = false
      })
  })
}

async function loadQuota(userId: string) {
  loading.value = true
  try {
    const quota = await ChatUserApi.getChatUserQuota(userId)
    // 避免快速切换用户时旧响应覆盖新用户表单
    if (pendingUserIds.value.length !== 1 || pendingUserIds.value[0] !== userId) return
    Object.assign(quotaSettingsForm, {
      quotaType: quota.quota_type,
      periodType: quota.period_type ?? PERIOD_TYPE.MONTH,
      periodValue: quota.period_value ?? 1,
      tokenLimit: quota.token_limit == null ? 10_000_000 : Math.round(quota.token_limit / 1000),
    })
  } catch {
    // 请求层已提示错误；保留默认表单，用户可自行设置后再保存
  } finally {
    loading.value = false
  }
}

async function open(chatUserIdOrIds: string | string[]) {
  const ids = Array.isArray(chatUserIdOrIds) ? chatUserIdOrIds : [chatUserIdOrIds]
  pendingUserIds.value = ids
  dialogVisible.value = true
  if (ids.length === 1) {
    await loadQuota(ids[0]!)
  }
}

function resetForm() {
  Object.assign(quotaSettingsForm, { periodType: PERIOD_TYPE.MONTH, periodValue: 1, quotaType: QUOTA_TYPE.UNLIMITED, tokenLimit: 10_000_000 })
}

function resetData() {
  resetForm()
  pendingUserIds.value = []
  loading.value = false
  submitting.value = false
  quotaSettingsFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('chatUser.quota.title')" @closed="resetData">
    <el-form
      ref="quotaSettingsFormRef"
      :model="quotaSettingsForm"
      :rules="quotaSettingsRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      v-loading="loading"
      @submit.prevent
    >
      <el-form-item :label="t('chatUser.quota.method.label')">
        <el-radio-group v-model="quotaSettingsForm.quotaType">
          <el-radio :value="QUOTA_TYPE.UNLIMITED">{{ t('chatUser.quota.method.unlimited') }}</el-radio>
          <el-radio :value="QUOTA_TYPE.PERIODIC">{{ t('chatUser.quota.method.periodic') }}</el-radio>
        </el-radio-group>
      </el-form-item>

      <template v-if="quotaSettingsForm.quotaType === QUOTA_TYPE.PERIODIC">
        <el-form-item :label="t('chatUser.quota.period.label')" prop="periodValue">
          <div class="flex-align-center gap-2">
            <span>{{ t('common.schedule.every') }}</span>
            <el-input-number v-model="quotaSettingsForm.periodValue" :min="1" :max="365" class="w-40!" align="left" controls-position="right" />
            <el-select v-model="quotaSettingsForm.periodType" class="w-40!">
              <el-option v-for="periodType in periodTypeOptions" :key="periodType.value" :label="periodType.label" :value="periodType.value" />
            </el-select>
          </div>
        </el-form-item>

        <el-form-item :label="t('chatUser.quota.tokenLimit.label')" prop="tokenLimit">
          <el-input-number v-model="quotaSettingsForm.tokenLimit" :min="1" align="left" controls-position="right" />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <!-- 取消配额设置 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存配额设置 -->
      <el-button :loading="submitting" type="primary" @click="submitQuotaSettings">{{ t('common.actions.comfirm') }}</el-button>
    </template>
  </MkDialog>
</template>
