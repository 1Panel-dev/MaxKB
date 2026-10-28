<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import UserGroupsApi from '@/api/admin/system/user-groups'
import CommonSystemApi from '@/api/admin/system/common'
import type { CommonUserOption } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{ workspaceId: string; currentGroup?: { id: string; name: string } }>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const formRules: FormRules = { userIds: [{ required: true, message: '请选择用户', trigger: 'change' }] }
const memberForm = reactive<{ userIds: string[] }>({ userIds: [] })

/* 成员选项 */
const optionsLoading = ref(false)
const userOptions = ref<CommonUserOption[]>([])
const allUserOptions = ref<CommonUserOption[]>([])
let searchTimer: ReturnType<typeof setTimeout> | null = null
function loadUserOptions(query = '') {
  const keyword = query.trim()
  optionsLoading.value = true
  CommonSystemApi.getWorkspaceMembers(props.workspaceId, keyword ? { nick_name: keyword } : undefined)
    .then((users) => {
      userOptions.value = users
      if (!keyword) allUserOptions.value = users
    })
    .finally(() => {
      optionsLoading.value = false
    })
}

function handleRemoteSearch(query: string) {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
  const keyword = query.trim()
  if (!keyword) {
    // Select 聚焦会触发空关键词搜索，复用首次列表以避免加载态导致下拉浮层重绘。
    userOptions.value = allUserOptions.value
    return
  }
  searchTimer = setTimeout(() => {
    searchTimer = null
    loadUserOptions(keyword)
  }, 300)
}

function submit() {
  const groupId = props.currentGroup?.id
  if (!groupId) return

  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    UserGroupsApi.postSystemUserGroupMembers(props.workspaceId, groupId, memberForm.userIds)
      .then(() => {
        MsgSuccess('添加成功')
        emit('refresh')
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open() {
  visible.value = true
  loadUserOptions()
}

function resetData() {
  memberForm.userIds = []
  loading.value = false
  optionsLoading.value = false
  userOptions.value = []
  allUserOptions.value = []
  formRef.value?.clearValidate()
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="添加成员" @closed="resetData">
    <el-form ref="formRef" :model="memberForm" :rules="formRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="用户名/姓名" prop="userIds">
        <el-select
          v-model="memberForm.userIds"
          class="w-full"
          filterable
          remote
          reserve-keyword
          multiple
          :remote-method="handleRemoteSearch"
          :loading="optionsLoading"
          placeholder="请选择用户名或姓名"
        >
          <el-option v-for="user in userOptions" :key="user.id" :label="user.nick_name" :value="user.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </MkDialog>
</template>
