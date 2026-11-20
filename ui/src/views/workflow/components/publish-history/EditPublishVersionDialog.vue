<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'EditPublishVersionDialog' })

const { t } = useI18n({ useScope: 'global' })

const props = withDefaults(defineProps<{ saving?: boolean; mode?: 'edit' | 'publish' }>(), { mode: 'edit' })
const emit = defineEmits<{ submit: [payload: WorkflowVersionPayload] }>()
const visible = ref(false)
/** 表单内部使用 description 命名，提交时映射为后端字段 publish_desc。 */
const versionForm = reactive<{ name: string; description: string }>({ name: '', description: '' })
const formRef = useTemplateRef<FormInstance>('formRef')
const rules = computed<FormRules<{ name: string; description: string }>>(() => ({
  name: [
    { required: true, whitespace: true, message: t('common.title.requiredMessage'), trigger: 'blur' },
    { max: 64, message: t('workflow.publishHistory.titleLengthMessage', { max: 64 }), trigger: 'blur' },
  ],
  description: [{ max: 1000, message: t('workflow.publishHistory.descriptionLengthMessage', { max: 1000 }), trigger: 'blur' }],
}))

/* 编辑副本并校验，接口提交和成功关闭由业务组件处理。 */
function open(version?: WorkflowVersion) {
  if (props.mode === 'edit' && version) {
    versionForm.name = version.name || datetimeFormat(version.create_time)
    versionForm.description = version.publish_desc ?? ''
  }
  visible.value = true
}

function handleSubmit() {
  if (props.saving) return
  formRef.value?.validate((valid) => {
    if (!valid || props.saving) return
    emit('submit', { name: versionForm.name.trim(), publish_desc: versionForm.description })
  })
}

function close() {
  visible.value = false
}

function resetForm() {
  versionForm.name = ''
  versionForm.description = ''
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="mode === 'publish' ? t('workflow.publishHistory.publishTitle') : t('common.actions.edit')" @closed="resetForm">
    <el-form
      ref="formRef"
      :model="versionForm"
      :rules="rules"
      :validate-on-rule-change="false"
      v-loading="saving"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('common.title.label')" prop="name">
        <el-input v-model="versionForm.name" :placeholder="t('common.title.placeholder')" :maxlength="64" show-word-limit />
      </el-form-item>
      <el-form-item :label="t('workflow.publishHistory.descriptionLabel')" prop="description">
        <el-input
          v-model="versionForm.description"
          type="textarea"
          :placeholder="t('common.placeholders.input')"
          :autosize="{ minRows: 4, maxRows: 8 }"
          :maxlength="1000"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消 -->
      <el-button plain :disabled="saving" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交版本内容 -->
      <el-button type="primary" :loading="saving" @click="handleSubmit">{{ t('common.actions.publish') }}</el-button>
    </template>
  </MkDialog>
</template>
