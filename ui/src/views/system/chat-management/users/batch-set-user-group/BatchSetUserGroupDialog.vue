<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BatchSetChatUserGroupsRequest, ListItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserApi from '@/api/admin/system/chat-management/chat-user'
import ChatUserGroupsApi from '@/api/admin/system/chat-management/chat-user-groups'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'BatchSetUserGroupDialog' })

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ refresh: [] }>()

const batchGroupFormRef = ref<FormInstance>()
const dialogVisible = ref(false)
const submitting = ref(false)
const userGroupOptionsLoading = ref(false)
const userGroupOptions = ref<ListItem[]>([])
const batchGroupForm = reactive<BatchSetChatUserGroupsRequest>({ ids: [], is_append: true, user_group_ids: [] })
const batchGroupFormRules = computed<FormRules<BatchSetChatUserGroupsRequest>>(() => ({
  user_group_ids: [{ required: true, type: 'array', min: 1, message: t('userGroup.requiredMessage'), trigger: 'change' }],
}))

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
        MsgSuccess(t('common.messages.saveSuccess'))
        emit('refresh')
        dialogVisible.value = false
      })
      .finally(() => {
        submitting.value = false
      })
  })
}

function open(userIds: string[]) {
  batchGroupForm.ids = [...userIds]
  loadUserGroupOptions()
  dialogVisible.value = true
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
  <MkDialog v-model="dialogVisible" :title="t('userGroup.set')" @closed="resetData">
    <el-form
      ref="batchGroupFormRef"
      :model="batchGroupForm"
      :rules="batchGroupFormRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('user.assignment.label')">
        <el-radio-group v-model="batchGroupForm.is_append">
          <el-radio :value="true">{{ t('user.assignment.append') }}</el-radio>
          <el-radio :value="false">{{ t('user.assignment.replace') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item :label="t('userGroup.title')" prop="user_group_ids">
        <el-select
          v-model="batchGroupForm.user_group_ids"
          class="w-full"
          :loading="userGroupOptionsLoading"
          clearable
          filterable
          multiple
          :placeholder="t('userGroup.placeholder')"
          fit-input-width
        >
          <el-option v-for="userGroup in userGroupOptions" :key="userGroup.id" :label="userGroup.name" :value="userGroup.id" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消批量设置用户组 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存用户组设置 -->
      <el-button type="primary" :loading="submitting" @click="submitBatchSetUserGroups">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
