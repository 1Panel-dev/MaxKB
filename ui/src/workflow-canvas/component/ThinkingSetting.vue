<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ReasoningSettingData } from '@/workflow-canvas/types'
import type { FormInstance } from 'element-plus'

defineOptions({ name: 'ThinkingSetting' })
const { t } = useI18n({ useScope: 'global' })

const setting = defineModel<ReasoningSettingData>({ required: true })

// 思考过程配置：打开时创建草稿，校验通过后写回。
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<ReasoningSettingData>({
  reasoning_content_enable: false,
  reasoning_content_end: '</think>',
  reasoning_content_start: '<think>',
})

function open() {
  formData.value = cloneDeep(setting.value)
  visible.value = true
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    setting.value = cloneDeep(formData.value)
    visible.value = false
  })
}

function resetData() {
  formData.value = {
    reasoning_content_enable: false,
    reasoning_content_end: '</think>',
    reasoning_content_start: '<think>',
  }
  formRef.value?.clearValidate()
}
</script>

<template>
  <!-- 打开思考标签设置 -->
  <el-button text type="primary" @click="open">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="visible" :title="t('common.labels.settings')" @closed="resetData">
    <template #subtitle>{{ t('workflow.thinking.description') }}</template>
    <el-form ref="formRef" :model="formData" class="grid grid-cols-2 gap-4" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item :label="t('workflow.thinking.start')">
        <el-input v-model="formData.reasoning_content_start" type="textarea" :rows="5" placeholder="<think>" />
      </el-form-item>
      <el-form-item :label="t('workflow.thinking.end')">
        <el-input v-model="formData.reasoning_content_end" type="textarea" :rows="5" placeholder="</think>" />
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消思考标签设置 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存思考标签设置 -->
      <el-button type="primary" @click="submit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
