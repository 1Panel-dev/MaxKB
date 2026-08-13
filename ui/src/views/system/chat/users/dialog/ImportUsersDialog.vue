<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserApi from '@/api/admin/system/chat-user'
import {
  LOGIN_METHOD,
  type ChatUserSyncConflict,
  type OptionItem,
  type LoginMethod,
} from '@/api/types'
import { LOGIN_METHOD_LABELS } from '@/constants/auth'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ImportUsersDialog' })

const emit = defineEmits<{
  refresh: []
}>()

interface ImportUsersForm {
  syncType: string
}

const dialogVisible = ref(false)

const importing = ref(false)
const importUsersFormRef = ref<FormInstance>()
const syncTypeOptions = ref<OptionItem<string>[]>([])
const importUsersForm = reactive<ImportUsersForm>({ syncType: '' })
const importUsersFormRules: FormRules<ImportUsersForm> = {
  syncType: [{ required: true, message: '请选择用户来源', trigger: 'change' }],
}

/* 获取导入用户的来源类型 */
const syncTypesLoading = ref(false)
function loadSyncTypes() {
  syncTypesLoading.value = true
  return ChatUserApi.getChatUserSyncTypes()
    .then((syncTypes) => {
      syncTypeOptions.value = syncTypes.map((syncType) => ({
        label:
          syncType === LOGIN_METHOD.LOCAL
            ? '系统用户'
            : LOGIN_METHOD_LABELS[syncType as LoginMethod],
        value: syncType,
      }))
      importUsersForm.syncType = syncTypeOptions.value[0]?.value ?? ''
    })
    .finally(() => {
      syncTypesLoading.value = false
    })
}

function formatConflictMessage(conflicts: ChatUserSyncConflict[]) {
  return conflicts
    .map((conflict) => {
      const conflictLabel =
        conflict.type === 'username'
          ? '用户名已存在'
          : conflict.type === 'nick_name'
            ? '姓名已存在'
            : `${conflict.type} 冲突`
      return `${conflictLabel}：${conflict.users.join('、')}`
    })
    .join('；')
}

/* 导入用户 */
function submitImportUsers() {
  if (!importUsersFormRef.value) return

  importUsersFormRef.value.validate((valid) => {
    if (!valid) return

    importing.value = true
    return ChatUserApi.postSyncChatUsers(importUsersForm.syncType)
      .then((result) => {
        const conflictMessage = formatConflictMessage(result.conflict_users ?? [])
        MsgSuccess(
          `成功导入 ${result.success_count} 个用户${conflictMessage ? `，${conflictMessage}` : ''}`,
        )
        emit('refresh')
        close()
      })
      .finally(() => {
        importing.value = false
      })
  })
}

function open() {
  dialogVisible.value = true
  loadSyncTypes()
}

function close() {
  dialogVisible.value = false
  resetData()
}

function resetData() {
  importUsersForm.syncType = ''
  syncTypeOptions.value = []
  syncTypesLoading.value = false
  importing.value = false
  importUsersFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="导入用户" @closed="resetData">
    <template #subtitle>
      从已配置的用户来源同步对话用户，已存在的用户名或姓名不会重复导入。
    </template>

    <el-form
      ref="importUsersFormRef"
      :model="importUsersForm"
      :rules="importUsersFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitImportUsers"
    >
      <el-form-item label="用户来源" prop="syncType">
        <el-select
          v-model="importUsersForm.syncType"
          class="w-full"
          :loading="syncTypesLoading"
          placeholder="请选择用户来源"
        >
          <el-option
            v-for="syncTypeOption in syncTypeOptions"
            :key="syncTypeOption.value"
            :label="syncTypeOption.label"
            :value="syncTypeOption.value"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="importing" @click="submitImportUsers">导入</el-button>
    </template>
  </MkDialog>
</template>
