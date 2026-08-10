<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatGroupsApi from '@/api/admin/system/chat-user-groups'
import ChatUserApi from '@/api/admin/system/chat-user'
import type { ChatUserBase, ListItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{
  currentGroup?: ListItem
}>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const optionsLoading = ref(false)
const formRef = ref<FormInstance>()
const userOptions = ref<ChatUserBase[]>([])
const memberForm = reactive<{ userIds: string[] }>({ userIds: [] })
const formRules: FormRules = {
  userIds: [{ required: true, message: '请选择对话用户', trigger: 'change' }],
}

function open() {
  visible.value = true
  optionsLoading.value = true
  return ChatUserApi.getChatUser()
    .then((users) => {
      userOptions.value = users
    })
    .finally(() => {
      optionsLoading.value = false
    })
}

function submit() {
  const groupId = props.currentGroup?.id
  if (!groupId) return

  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    ChatGroupsApi.postChatUserGroupMembers(groupId, memberForm.userIds)
      .then(() => {
        MsgSuccess('添加成功')
        emit('refresh')
        close()
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function close() {
  visible.value = false
  resetData()
}

function resetData() {
  memberForm.userIds = []
  loading.value = false
  optionsLoading.value = false
  userOptions.value = []
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="添加成员" @closed="resetData">
    <el-form ref="formRef" :model="memberForm" :rules="formRules" label-position="top">
      <el-form-item label="对话用户" prop="userIds">
        <el-select
          v-model="memberForm.userIds"
          class="w-full"
          filterable
          multiple
          collapse-tags
          collapse-tags-tooltip
          :loading="optionsLoading"
          placeholder="请选择用户名或姓名"
        >
          <el-option
            v-for="user in userOptions"
            :key="user.id"
            :label="user.nick_name"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </MkDialog>
</template>
