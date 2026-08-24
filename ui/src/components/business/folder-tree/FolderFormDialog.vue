<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import FolderApi from '@/api/admin/workspace/folder'
import type { FolderItem, FolderSource } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'FolderFormDialog' })

const { user } = useStore()

const props = defineProps<{
  title: string
  source: FolderSource
}>()

const emit = defineEmits<{
  refresh: [folder: FolderItem, isEdit: boolean]
}>()

const folderFormRef = useTemplateRef<FormInstance>('folderFormRef')
const visible = ref(false)
const editId = ref('')
const folderForm = reactive({
  desc: '',
  name: '',
  parent_id: '',
})

const rules: FormRules<typeof folderForm> = {
  name: [{ message: '请输入文件夹名称', required: true, trigger: 'blur' }],
}

const loading = ref(false)
function handleSubmit() {
  folderFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    const isEdit = Boolean(editId.value)
    const request = isEdit
      ? FolderApi.putFolder(editId.value, props.source, folderForm)
      : FolderApi.postFolder(props.source, folderForm)

    return request
      .then((folder) => {
        const refreshCurrentUser = isEdit ? Promise.resolve() : user.loadCurrentUser()
        return refreshCurrentUser.then(() => {
          MsgSuccess(isEdit ? '保存成功' : '创建成功')
          visible.value = false
          emit('refresh', folder, isEdit)
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open(id: string, folder?: FolderItem) {
  if (folder) {
    //  编辑当前id
    editId.value = folder?.id
    folderForm.name = folder?.name ?? ''
    folderForm.desc = folder?.desc ?? ''
    folderForm.parent_id = folder.parent_id ?? ''
  } else {
    //  给当前id添加子id
    folderForm.parent_id = id
  }

  visible.value = true
}

function resetData() {
  editId.value = ''
  folderForm.desc = ''
  folderForm.name = ''
  folderForm.parent_id = ''
  folderFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="title" @closed="resetData">
    <el-form
      ref="folderFormRef"
      :model="folderForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="folderForm.name"
          maxlength="64"
          placeholder="请输入名称"
          show-word-limit
          @blur="folderForm.name = folderForm.name.trim()"
        />
      </el-form-item>
      <el-form-item label="描述" prop="desc">
        <el-input
          v-model="folderForm.desc"
          placeholder="请输入描述"
          maxlength="128"
          show-word-limit
          :autosize="{ minRows: 3 }"
          type="textarea"
          @blur="folderForm.desc = folderForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDialog>
</template>
