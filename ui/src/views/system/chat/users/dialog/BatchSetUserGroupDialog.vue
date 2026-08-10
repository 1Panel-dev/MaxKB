<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserApi from '@/api/admin/system/chat-user'
import ChatUserGroupsApi from '@/api/admin/system/chat-user-groups'
import type { BatchSetChatUserGroupsRequest, ListItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'BatchSetUserGroupDialog' })

const emit = defineEmits<{
  refresh: []
}>()

const batchGroupFormRef = ref<FormInstance>()
const dialogVisible = ref(false)
const submitting = ref(false)
const userGroupOptionsLoading = ref(false)
const userGroupOptions = ref<ListItem[]>([])
const batchGroupForm = reactive<BatchSetChatUserGroupsRequest>({
  ids: [],
  is_append: true,
  user_group_ids: [],
})
const batchGroupFormRules: FormRules<BatchSetChatUserGroupsRequest> = {
  user_group_ids: [
    { required: true, type: 'array', min: 1, message: '请选择用户组', trigger: 'change' },
  ],
}

/* 用户组选项 */
function loadUserGroupOptions() {
  userGroupOptionsLoading.value = true
  return ChatUserGroupsApi.getChatUserGroups()
    .then((groups) => {
      userGroupOptions.value = groups
    })
    .finally(() => {
      userGroupOptionsLoading.value = false
    })
}

/* 批量设置用户组 */
function submitBatchSetUserGroups() {
  if (!batchGroupFormRef.value) return

  batchGroupFormRef.value.validate((valid) => {
    if (!valid) return

    submitting.value = true
    return ChatUserApi.postBatchSetChatUserGroups({ ...batchGroupForm })
      .then(() => {
        MsgSuccess('设置成功')
        emit('refresh')
        close()
      })
      .finally(() => {
        submitting.value = false
      })
  })
}

function open(userIds: string[]) {
  resetData()
  batchGroupForm.ids = [...userIds]
  dialogVisible.value = true
  loadUserGroupOptions()
}

function close() {
  dialogVisible.value = false
  resetData()
}

function resetData() {
  Object.assign(batchGroupForm, { ids: [], is_append: true, user_group_ids: [] })
  submitting.value = false
  userGroupOptionsLoading.value = false
  userGroupOptions.value = []
  batchGroupFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="设置用户组" align-center @closed="resetData">
    <el-form
      ref="batchGroupFormRef"
      :model="batchGroupForm"
      :rules="batchGroupFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitBatchSetUserGroups"
    >
      <el-form-item label="设置方式">
        <el-radio-group v-model="batchGroupForm.is_append">
          <el-radio :value="true">追加</el-radio>
          <el-radio :value="false">替换</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="用户组" prop="user_group_ids">
        <el-select
          v-model="batchGroupForm.user_group_ids"
          class="w-full"
          :loading="userGroupOptionsLoading"
          clearable
          filterable
          multiple
          placeholder="请选择用户组"
        >
          <el-option
            v-for="userGroup in userGroupOptions"
            :key="userGroup.id"
            :label="userGroup.name"
            :value="userGroup.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submitBatchSetUserGroups">
        保存
      </el-button>
    </template>
  </MkDialog>
</template>
