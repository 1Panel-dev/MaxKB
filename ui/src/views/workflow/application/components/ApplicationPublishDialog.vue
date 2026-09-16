<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationDetail } from '@/api/types'
import ApplicationApi from '@/api/admin/workspace/application/application.ts'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ApplicationPublishDialog' })

const props = defineProps<{ resourceId: string }>()
const emit = defineEmits<{ published: [application: ApplicationDetail] }>()

const visible = ref(false)
const saving = ref(false)
const publishForm = reactive<{ publish_name: string; publish_desc: string }>({ publish_name: '', publish_desc: '' })
const formRef = useTemplateRef<FormInstance>('formRef')
const rules: FormRules = {
  publish_name: [
    { required: true, whitespace: true, message: '请输入发布标题', trigger: 'blur' },
    { max: 64, message: '发布标题最多 64 个字符', trigger: 'blur' },
  ],
  publish_desc: [{ max: 1000, message: '更新说明最多 1000 个字符', trigger: 'blur' }],
}

function open() {
  visible.value = true
}

function handleSubmit() {
  if (saving.value) return
  formRef.value?.validate((valid) => {
    if (!valid) return
    saving.value = true
    return ApplicationApi.putApplicationPublish(props.resourceId, publishForm.publish_name.trim(), publishForm.publish_desc)
      .then((application) => {
        emit('published', application)
        visible.value = false
        MsgSuccess('发布成功')
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
  publishForm.publish_name = ''
  publishForm.publish_desc = ''
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    class="application-publish-dialog"
    title="发布"
    width="600"
    align-center
    :before-close="handleClose"
    :show-close="!saving"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="publishForm" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent="handleSubmit">
      <el-form-item label="发布标题" prop="publish_name">
        <el-input v-model="publishForm.publish_name" placeholder="请输入发布标题" :maxlength="64" show-word-limit :disabled="saving" />
      </el-form-item>
      <el-form-item label="更新说明" prop="publish_desc" class="mb-0!">
        <el-input
          v-model="publishForm.publish_desc"
          type="textarea"
          placeholder="请输入更新说明（选填）"
          :rows="4"
          :maxlength="1000"
          show-word-limit
          resize="none"
          :disabled="saving"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消发布 -->
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <!-- 提交发布 -->
      <el-button type="primary" :loading="saving" @click="handleSubmit">发布</el-button>
    </template>
  </MkDialog>
</template>

<style scoped>
/* 内容较短时按表单高度展示，避免滚动容器继承视口高度。 */
:global(.application-publish-dialog .el-dialog__body > .el-scrollbar),
:global(.application-publish-dialog .el-dialog__body > .el-scrollbar > .el-scrollbar__wrap) {
  height: auto;
}
</style>
