<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { UserInputSetting } from '../../types'
import type { FormField } from '@/components/mk-dynamics-form'
import { exposedInputTypes } from './constant'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ fields: FormField[] }>()
const emit = defineEmits<{ submit: [setting: UserInputSetting] }>()
const settingDialogVisible = ref(false)
const currentSetting = ref<UserInputSetting>({ exposed_fields: [], menu_title: t('workflow.userInput.title') })
const exposedFieldOptions = computed(() => props.fields.filter(({ input_type }) => exposedInputTypes.includes(input_type)))

function formatLabel(label: FormField['label'], fallback = '') {
  return typeof label === 'string' ? label : (label?.label ?? fallback)
}

function resetData() {
  currentSetting.value = { exposed_fields: [], menu_title: t('workflow.userInput.title') }
}

function open(setting: UserInputSetting) {
  currentSetting.value = cloneDeep(setting)
  settingDialogVisible.value = true
}

function submitSetting() {
  emit('submit', cloneDeep(currentSetting.value))
  settingDialogVisible.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="settingDialogVisible" :title="t('common.labels.settings')" @closed="resetData">
    <el-form :validate-on-rule-change="false" :model="currentSetting" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item>
        <template #label>
          <span class="flex-align-center gap-1">
            <span>{{ t('workflow.userInput.exposedFields.label') }}</span>
            <MkTooltip placement="right" :content="t('workflow.userInput.exposedFields.description')">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </span>
        </template>
        <el-select v-model="currentSetting.exposed_fields" multiple :placeholder="t('common.placeholders.select')">
          <el-option v-for="field in exposedFieldOptions" :key="field.field" :label="formatLabel(field.label, field.field)" :value="field.field" />
        </el-select>
      </el-form-item>
      <el-form-item
        :label="t('workflow.userInput.menuTitle.label')"
        prop="menu_title"
        :rules="[{ whitespace: true, required: true, message: t('common.validation.inputRequired'), trigger: 'blur' }]"
      >
        <el-input v-model="currentSetting.menu_title" maxlength="64" show-word-limit :placeholder="t('common.placeholders.input')" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消参数编辑 -->
      <el-button plain @click="settingDialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确认参数编辑 -->
      <el-button type="primary" @click="submitSetting">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
