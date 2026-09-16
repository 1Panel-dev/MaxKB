<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'EditPublishVersionDialog' })

const props = withDefaults(defineProps<{ saving?: boolean; mode?: 'edit' | 'publish' }>(), { mode: 'edit' })
const emit = defineEmits<{ submit: [payload: WorkflowVersionPayload] }>()
const visible = ref(false)
/** 表单内部使用 description 命名，提交时映射为后端字段 publish_desc。 */
const versionForm = reactive<{ name: string; description: string }>({ name: '', description: '' })
const formRef = useTemplateRef<FormInstance>('formRef')
const rules: FormRules<{ name: string; description: string }> = {
  name: [
    { required: true, whitespace: true, message: '请输入标题', trigger: 'blur' },
    { max: 64, message: '标题最多 64 个字符', trigger: 'blur' },
  ],
  description: [{ max: 1000, message: '更新说明最多 1000 个字符', trigger: 'blur' }],
}

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

function handleClose(done: () => void) {
  if (!props.saving) done()
}

function resetForm() {
  versionForm.name = ''
  versionForm.description = ''
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="mode === 'publish' ? '发布内容' : '编辑'" align-center :before-close="handleClose" @closed="resetForm">
    <el-form
      ref="formRef"
      :model="versionForm"
      :rules="rules"
      :disabled="saving"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
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
      <!-- 取消 -->
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <!-- 提交版本内容 -->
      <el-button type="primary" :loading="saving" @click="handleSubmit">发布</el-button>
    </template>
  </MkDialog>
</template>
