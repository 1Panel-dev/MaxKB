<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ToolFieldConfig } from '../../types'
import type { FormInstance } from 'element-plus'

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [data: ToolFieldConfig] }>()
const formRef = useTemplateRef<FormInstance>('formRef')
const dialogVisible = ref(false)
const form = ref<ToolFieldConfig>({ title: t('workflow.userInput.title') })

function resetData() {
  form.value = { title: t('workflow.userInput.title') }
  formRef.value?.clearValidate()
}

function open(config: ToolFieldConfig) {
  form.value = cloneDeep(config)
  dialogVisible.value = true
}

function submitTitle() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(form.value)))
    .catch(() => {})
}

function close() {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('common.labels.settings')" @closed="resetData">
    <el-form ref="formRef" :model="form" :validate-on-rule-change="false" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        :label="t('common.title.label')"
        prop="title"
        :rules="[{ whitespace: true, required: true, message: t('common.title.requiredMessage'), trigger: 'blur' }]"
      >
        <el-input v-model="form.title" maxlength="64" show-word-limit @blur="form.title = form.title.trim()" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消设置 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存标题 -->
      <el-button type="primary" @click="submitTitle">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
