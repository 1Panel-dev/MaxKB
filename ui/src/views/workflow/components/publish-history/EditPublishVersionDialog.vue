<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import type WorkflowVersionApi from '@/api/admin/workspace/application/workflow-version'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EditPublishVersionDialog' })

const props = defineProps<{ resourceId: string; api: typeof WorkflowVersionApi }>()
const emit = defineEmits<{ saved: [version: WorkflowVersion] }>()
const visible = ref(false)
const saving = ref(false)
const versionId = ref('')
const versionForm = reactive<WorkflowVersionPayload>({ name: '', description: '' })
const formRef = useTemplateRef<FormInstance>('formRef')
const rules: FormRules<WorkflowVersionPayload> = {
  name: [
    { required: true, whitespace: true, message: '请输入标题', trigger: 'blur' },
    { max: 64, message: '标题最多 64 个字符', trigger: 'blur' },
  ],
  description: [{ max: 1000, message: '更新说明最多 1000 个字符', trigger: 'blur' }],
}

/* 版本编辑：只保存副本，接口成功后通知历史列表更新。 */
function open(version: WorkflowVersion) {
  versionId.value = version.id
  versionForm.name = version.name || datetimeFormat(version.create_time)
  versionForm.description = version.description ?? ''
  visible.value = true
}

function handleSubmit() {
  if (saving.value) return
  formRef.value?.validate((valid) => {
    if (!valid) return
    saving.value = true
    return props.api
      .putWorkflowVersion(props.resourceId, versionId.value, {
        name: versionForm.name.trim(),
        description: versionForm.description,
      })
      .then((version) => {
        emit('saved', version)
        visible.value = false
        MsgSuccess('修改成功')
      })
      .finally(() => {
        saving.value = false
      })
  })
}

function handleClose(done: () => void) {
  if (!saving.value) done()
}

function resetForm() {
  versionId.value = ''
  versionForm.name = ''
  versionForm.description = ''
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    class="workflow-version-edit-dialog"
    title="编辑"
    width="600"
    align-center
    :before-close="handleClose"
    :show-close="!saving"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="versionForm" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent="handleSubmit">
      <el-form-item label="标题" prop="name">
        <el-input v-model="versionForm.name" placeholder="请输入标题" :maxlength="64" show-word-limit :disabled="saving" />
      </el-form-item>
      <el-form-item label="更新说明" prop="description" class="mb-0!">
        <el-input
          v-model="versionForm.description"
          type="textarea"
          placeholder="请输入"
          :rows="4"
          :maxlength="1000"
          show-word-limit
          resize="none"
          :disabled="saving"
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

<style scoped>
/* 内容较短时按表单高度展示，避免滚动容器继承视口高度。 */
:global(.workflow-version-edit-dialog .el-dialog__body > .el-scrollbar),
:global(.workflow-version-edit-dialog .el-dialog__body > .el-scrollbar > .el-scrollbar__wrap) {
  height: auto;
}
</style>
