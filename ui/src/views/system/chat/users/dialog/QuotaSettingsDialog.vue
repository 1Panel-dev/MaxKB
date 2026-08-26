<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserApi from '@/api/admin/system/chat-user'
import { PERIOD_TYPE, QUOTA_TYPE } from '@/api/enums'
import type { ChatUserQuotaPayload, PeriodType, QuotaType } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'QuotaSettingsDialog' })

const emit = defineEmits<{
  refresh: []
}>()

interface QuotaSettingsForm {
  periodType: PeriodType
  periodValue: number
  quotaType: QuotaType
  tokenLimit: number
}

const periodTypeOptions: Array<{ label: string; value: PeriodType }> = [
  { label: '天', value: PERIOD_TYPE.DAY },
  { label: '周', value: PERIOD_TYPE.WEEK },
  { label: '月', value: PERIOD_TYPE.MONTH },
]

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
const quotaSettingsRules: FormRules<QuotaSettingsForm> = {
  periodValue: [{ required: true, message: '请输入周期', trigger: 'change' }],
  tokenLimit: [{ required: true, message: '请输入 Tokens 上限', trigger: 'change' }],
}

function resetForm() {
  Object.assign(quotaSettingsForm, {
    periodType: PERIOD_TYPE.MONTH,
    periodValue: 1,
    quotaType: QUOTA_TYPE.UNLIMITED,
    tokenLimit: 10_000_000,
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
      tokenLimit: quota.token_limit ?? 10_000_000,
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
  resetForm()
  dialogVisible.value = true
  quotaSettingsFormRef.value?.clearValidate()
  if (ids.length === 1) {
    await loadQuota(ids[0]!)
  }
}

function buildPayload(): ChatUserQuotaPayload {
  if (quotaSettingsForm.quotaType === QUOTA_TYPE.UNLIMITED) {
    return {
      quota_type: QUOTA_TYPE.UNLIMITED,
      period_type: null,
      period_value: null,
      token_limit: null,
    }
  }
  return {
    quota_type: QUOTA_TYPE.PERIODIC,
    period_type: quotaSettingsForm.periodType,
    period_value: quotaSettingsForm.periodValue,
    token_limit: quotaSettingsForm.tokenLimit,
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
        MsgSuccess('配额设置成功')
        emit('refresh')
        dialogVisible.value = false
      })
      .finally(() => {
        submitting.value = false
      })
  })
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
  <MkDialog v-model="dialogVisible" title="配额设置" width="480" align-center @closed="resetData">
    <el-form
      ref="quotaSettingsFormRef"
      :model="quotaSettingsForm"
      :rules="quotaSettingsRules"
      label-position="top"
      require-asterisk-position="right"
      v-loading="loading"
      @submit.prevent="submitQuotaSettings"
    >
      <el-form-item label="设置方式">
        <el-radio-group v-model="quotaSettingsForm.quotaType">
          <el-radio :value="QUOTA_TYPE.UNLIMITED">不限额</el-radio>
          <el-radio :value="QUOTA_TYPE.PERIODIC">按周期限制</el-radio>
        </el-radio-group>
      </el-form-item>

      <template v-if="quotaSettingsForm.quotaType === QUOTA_TYPE.PERIODIC">
        <el-form-item label="周期" prop="periodValue">
          <div class="flex items-center gap-2">
            <span>每</span>
            <el-input-number
              v-model="quotaSettingsForm.periodValue"
              :min="1"
              :max="365"
              class="w-40!"
              align="left"
              controls-position="right"
            />
            <el-select v-model="quotaSettingsForm.periodType" class="w-40!">
              <el-option
                v-for="periodType in periodTypeOptions"
                :key="periodType.value"
                :label="periodType.label"
                :value="periodType.value"
              />
            </el-select>
          </div>
        </el-form-item>

        <el-form-item label="Tokens 上限（单位：K）" prop="tokenLimit">
          <el-input-number
            v-model="quotaSettingsForm.tokenLimit"
            class="w-full!"
            :min="1"
            align="left"
            controls-position="right"
          />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button :loading="submitting" type="primary" @click="submitQuotaSettings">确定</el-button>
    </template>
  </MkDialog>
</template>
