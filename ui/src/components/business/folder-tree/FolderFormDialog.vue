<script setup lang="ts">
import { computed, nextTick, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { WorkspaceFolder } from '@/api/types'
import type { FolderFormSubmit } from './types'

defineOptions({ name: 'FolderFormDialog' })

defineProps<{
  loading: boolean
}>()

const emit = defineEmits<{
  submit: [form: FolderFormSubmit]
}>()

interface FolderForm {
  desc: string
  name: string
  parent_id: string
}

const folderFormRef = useTemplateRef<FormInstance>('folderFormRef')
const visible = ref(false)
const editingFolderId = ref('')
const folderForm = reactive<FolderForm>({
  desc: '',
  name: '',
  parent_id: '',
})

const dialogTitle = computed(() => (editingFolderId.value ? '编辑文件夹' : '创建文件夹'))
const rules: FormRules<FolderForm> = {
  name: [{ message: '请输入文件夹名称', required: true, trigger: 'blur' }],
}

function resetData() {
  editingFolderId.value = ''
  folderForm.desc = ''
  folderForm.name = ''
  folderForm.parent_id = ''
  folderFormRef.value?.clearValidate()
}

function open(parentId: string, folder?: WorkspaceFolder) {
  resetData()
  editingFolderId.value = folder?.id ?? ''
  folderForm.desc = folder?.desc ?? ''
  folderForm.name = folder?.name ?? ''
  folderForm.parent_id = folder?.parent_id ?? parentId
  visible.value = true
  nextTick(() => folderFormRef.value?.clearValidate())
}

function close() {
  visible.value = false
  resetData()
}

function handleSubmit() {
  folderFormRef.value?.validate((valid) => {
    if (!valid) return
    emit('submit', {
      folderId: editingFolderId.value || undefined,
      payload: {
        desc: folderForm.desc.trim(),
        name: folderForm.name.trim(),
        parent_id: folderForm.parent_id,
      },
    })
  })
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog v-model="visible" :title="dialogTitle" width="600" @closed="resetData">
    <el-form
      ref="folderFormRef"
      :model="folderForm"
      :rules="rules"
      label-position="top"
      @submit.prevent
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="folderForm.name"
          maxlength="64"
          placeholder="请输入文件夹名称"
          show-word-limit
          @blur="folderForm.name = folderForm.name.trim()"
        />
      </el-form-item>
      <el-form-item label="描述" prop="desc">
        <el-input
          v-model="folderForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="200"
          placeholder="请输入文件夹描述"
          show-word-limit
          type="textarea"
          @blur="folderForm.desc = folderForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button :disabled="loading" @click="close">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ editingFolderId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDialog>
</template>
