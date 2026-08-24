<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import UserGroupsApi from '@/api/admin/system/user-groups'
import type { SystemUserGroup } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits<{
  refresh: [group: SystemUserGroup]
}>()

const props = defineProps<{
  workspaceId: string
}>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const groupForm = reactive<{ id?: string; name: string }>({ name: '' })
const formRules: FormRules = {
  name: [{ required: true, message: '请输入用户组名称', trigger: 'blur' }],
}

function open(group?: { id: string; name: string }) {
  if (group) {
    groupForm.id = group?.id
    groupForm.name = group?.name
  }
  visible.value = true
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    UserGroupsApi.postSystemUserGroup(props.workspaceId, { id: groupForm.id, name: groupForm.name })
      .then((group) => {
        MsgSuccess(groupForm.id ? '重命名成功' : '创建成功')
        emit('refresh', group)
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function resetData() {
  Object.assign(groupForm, { name: '' })
  loading.value = false
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="groupForm.id ? '重命名用户组' : '创建用户组'"
    @closed="resetData"
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
  </MkDialog>
</template>
