<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatGroupsApi from '@/api/admin/system/chat-user-groups'
import type { ListItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits<{
  refresh: [groupId?: string]
}>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const groupForm = reactive<{ id?: string; name: string }>({ name: '' })
const formRules: FormRules = {
  name: [{ required: true, message: '请输入用户组名称', trigger: 'blur' }],
}

function open(group?: ListItem) {
  if (group) {
    groupForm.id = group?.id
    groupForm.name = group?.name
  } else {
    Object.assign(groupForm, {
      name: '',
    })
  }
  visible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    ChatGroupsApi.postChatUserGroup({ ...groupForm })
      .then(() => {
        MsgSuccess(groupForm.id ? '重命名成功' : '创建成功')
        visible.value = false
        emit('refresh', groupForm?.id || undefined)
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
    v-model="visible"
    :title="groupForm.id ? '重命名用户组' : '创建用户组'"
    width="600px"
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form ref="formRef" :model="groupForm" :rules="formRules" label-position="top">
      <el-form-item label="用户组名称" prop="name">
        <el-input
          v-model="groupForm.name"
          maxlength="128"
          placeholder="请输入用户组名称"
          show-word-limit
          @keyup.enter="submit"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">
        {{ groupForm.id ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>
