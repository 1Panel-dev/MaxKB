<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatGroupsApi from '@/api/admin/system/chat-user-groups'
import ChatUserApi from '@/api/admin/system/chat-user'
import type { ListItem, ChatGroupMemberOption } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{
  currentGroup?: ListItem
}>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const optionsLoading = ref(false)
const formRef = ref<FormInstance>()
const userOptions = ref<ChatGroupMemberOption[]>([])
const memberForm = reactive<{ userIds: string[] }>({ userIds: [] })
const formRules: FormRules = {
  userIds: [{ required: true, message: '请选择对话用户', trigger: 'change' }],
}

function open() {
  memberForm.userIds = []
  visible.value = true
  optionsLoading.value = true
  nextTick(() => formRef.value?.clearValidate())
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
        visible.value = false
        emit('refresh')
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
    title="添加成员"
    width="600px"
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
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
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </el-dialog>
</template>
