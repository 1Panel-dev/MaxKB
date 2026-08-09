<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import WorkspaceApi from '@/api/admin/system/workspace'
import type { WorkspaceItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateOrUpdateWorkspaceDialog' })

const emit = defineEmits<{
  refresh: [workspaceId?: string]
}>()

const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const workspaceForm = reactive<WorkspaceItem>({ name: '' })
const workspaceRules: FormRules<WorkspaceItem> = {
  name: [{ required: true, message: '请输入工作空间名称', trigger: 'blur' }],
}

function open(workspace?: WorkspaceItem) {
  if (workspace) {
    workspaceForm.id = workspace?.id
    workspaceForm.name = workspace?.name
  } else {
    Object.assign(workspaceForm, {
      name: '',
    })
  }
  nextTick(() => formRef.value?.clearValidate())
  dialogVisible.value = true
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    WorkspaceApi.postWorkspace({ ...workspaceForm })
      .then(() => {
        MsgSuccess(workspaceForm.id ? '重命名成功' : '创建成功')
        emit('refresh', workspaceForm?.id || undefined)
        dialogVisible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="workspaceForm.id ? '重命名工作空间' : '创建工作空间'"
    width="600px"
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="formRef"
      :model="workspaceForm"
      :rules="workspaceRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="工作空间名称" prop="name">
        <el-input
          v-model="workspaceForm.name"
          maxlength="64"
          placeholder="请输入工作空间名称"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">
        {{ workspaceForm.id ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>
