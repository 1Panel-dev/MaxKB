<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'QuotaSettingsDialog' })

type QuotaType = 'UNLIMITED' | 'PERIODIC'
type PeriodType = 'DAY' | 'WEEK' | 'MONTH'

interface QuotaSettingsForm {
  periodType: PeriodType
  periodValue: number
  quotaType: QuotaType
  tokenLimit: number
}

interface QuotaSettingsSubmitPayload extends QuotaSettingsForm {
  userId: string
}

const emit = defineEmits<{
  submit: [settings: QuotaSettingsSubmitPayload]
}>()

const periodTypeOptions: Array<{ label: string; value: PeriodType }> = [
  { label: '天', value: 'DAY' },
  { label: '周', value: 'WEEK' },
  { label: '月', value: 'MONTH' },
]

const dialogVisible = ref(false)
const quotaSettingsFormRef = ref<FormInstance>()
const userId = ref('')
const quotaSettingsForm = reactive<QuotaSettingsForm>({
  periodType: 'MONTH',
  periodValue: 1,
  quotaType: 'UNLIMITED',
  tokenLimit: 10000000,
})
const quotaSettingsRules: FormRules<QuotaSettingsForm> = {
  periodValue: [{ required: true, message: '请输入周期', trigger: 'change' }],
  tokenLimit: [{ required: true, message: '请输入 Tokens 上限', trigger: 'change' }],
}

function open(chatUserId: string) {
  userId.value = chatUserId
  dialogVisible.value = true
}

function submitQuotaSettings() {
  quotaSettingsFormRef.value?.validate((valid) => {
    if (!valid) return

    emit('submit', {
      ...quotaSettingsForm,
      userId: userId.value,
    })
    dialogVisible.value = false
  })
}

function resetData() {
  Object.assign(quotaSettingsForm, {
    periodType: 'MONTH',
    periodValue: 1,
    quotaType: 'UNLIMITED',
    tokenLimit: 10_000_000,
  })
  userId.value = ''
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
      @submit.prevent="submitQuotaSettings"
    >
      <el-form-item label="设置方式">
        <el-radio-group v-model="quotaSettingsForm.quotaType">
          <el-radio value="UNLIMITED">不限额</el-radio>
          <el-radio value="PERIODIC">按周期限制</el-radio>
        </el-radio-group>
      </el-form-item>

      <template v-if="quotaSettingsForm.quotaType === 'PERIODIC'">
        <el-form-item label="周期" prop="periodValue">
          <div class="flex items-center gap-2">
            <span>每</span>
            <el-input-number
              v-model="quotaSettingsForm.periodValue"
              :min="1"
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
      <el-button type="primary" @click="submitQuotaSettings">确定</el-button>
    </template>
  </MkDialog>
</template>
