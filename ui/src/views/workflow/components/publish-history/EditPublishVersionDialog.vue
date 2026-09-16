<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'EditPublishVersionDialog' })

const props = defineProps<{ saving?: boolean }>()
const emit = defineEmits<{ submit: [payload: WorkflowVersionPayload] }>()
const visible = ref(false)
/** 表单内部使用 description 命名，提交时映射为后端字段 publish_desc。 */
const versionForm = reactive<{ name: string; description: string }>({ name: '', description: '' })
const formRef = useTemplateRef<FormInstance>('formRef')
const rules: FormRules<{ name: string; description: string }> = {
  name: [{ required: true, message: '请输入标题', trigger: 'blur' }],
}

/* 编辑副本并校验，接口提交和成功关闭由业务组件处理。 */
function open(version: WorkflowVersion) {
  versionForm.name = version.name || datetimeFormat(version.create_time)
  versionForm.description = version.publish_desc ?? ''
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
  <MkDialog v-model="visible" title="编辑" align-center @closed="resetForm">
    <el-form ref="formRef" :model="versionForm" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent="handleSubmit">
      <el-form-item label="标题" prop="name">
        <el-input v-model="versionForm.name" placeholder="请输入标题" :maxlength="64" show-word-limit />
      </el-form-item>
      <el-form-item label="更新说明" prop="description">
        <el-input
          v-model="versionForm.description"
          type="textarea"
          placeholder="请输入"
          :autosize="{ minRows: 4, maxRows: 8 }"
          :maxlength="1000"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消版本编辑 -->
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <!-- 提交版本编辑 -->
      <el-button type="primary" :loading="saving" @click="handleSubmit">发布</el-button>
    </template>
  </MkDialog>
</template>

<style scoped></style>
