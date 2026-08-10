<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserManageApi from '@/api/admin/system/user-manage'
import type { ListItem, BatchSetUserWorkspaceRolesRequest } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import UserRoleSetting from '../components/UserRoleSetting.vue'

defineOptions({ name: 'BatchSetUserRoleDialog' })

const { auth } = useStore()

const emit = defineEmits<{
  refresh: []
}>()

const batchRoleFormRef = ref<FormInstance>()
const dialogVisible = ref(false)

const submitting = ref(false)

const batchRoleForm = reactive<BatchSetUserWorkspaceRolesRequest>({
  ids: [],
  is_append: true,
  role_setting: [{ role_id: '', workspace_ids: [] }],
})

/* 角色与工作空间选项 */
const roleSettingOptionsLoading = ref(false)
const roleOptions = ref<ListItem[]>([])
const workspaceOptions = ref<ListItem[]>([])
function loadRoleSettingOptions() {
  roleSettingOptionsLoading.value = true
  const optionRequests: Promise<void>[] = [
    CurrentUserApi.getCurrentUserRoleList().then((roles) => {
      roleOptions.value = roles
    }),
  ]

  if (auth.isEE) {
    optionRequests.push(
      CurrentUserApi.getCurrentUserWorkspaceList().then((workspaces) => {
        workspaceOptions.value = workspaces
      }),
    )
  }

  return Promise.all(optionRequests).finally(() => {
    roleSettingOptionsLoading.value = false
  })
}

/* 批量设置角色 */
function submitBatchSetUserRoles() {
  if (!batchRoleFormRef.value) return

  batchRoleFormRef.value.validate((valid) => {
    if (!valid) return

    submitting.value = true
    const request = auth.isEE
      ? UserManageApi.postBatchSetUserWorkspaceRoles({
          ids: batchRoleForm.ids,
          is_append: batchRoleForm.is_append,
          role_setting: batchRoleForm.role_setting.map((assignment) => ({
            ...assignment,
            workspace_ids:
              roleOptions.value.find(({ id }) => id === assignment.role_id)?.type === 'ADMIN'
                ? ['None']
                : assignment.workspace_ids,
          })),
        })
      : UserManageApi.postBatchSetUserRoles({
          ids: batchRoleForm.ids,
          is_append: batchRoleForm.is_append,
          role_ids: batchRoleForm.role_setting.map((assignment) => assignment.role_id),
        })

    return request
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
  batchRoleForm.ids = [...userIds]
  dialogVisible.value = true
  loadRoleSettingOptions()
}

function close() {
  dialogVisible.value = false
  resetData()
}

function resetData() {
  Object.assign(batchRoleForm, {
    ids: [],
    is_append: true,
    role_setting: [{ role_id: '', workspace_ids: [] }],
  })
  roleSettingOptionsLoading.value = false
  submitting.value = false
  roleOptions.value = []
  workspaceOptions.value = []
  batchRoleFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="设置角色" align-center @closed="resetData">
    <el-form
      ref="batchRoleFormRef"
      :model="batchRoleForm"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitBatchSetUserRoles"
    >
      <el-form-item label="设置方式">
        <el-radio-group v-model="batchRoleForm.is_append">
          <el-radio :value="true">追加</el-radio>
          <el-radio :value="false">替换</el-radio>
        </el-radio-group>
      </el-form-item>

      <UserRoleSetting
        v-if="auth.isEE || auth.isPE"
        v-model="batchRoleForm.role_setting"
        :loading="roleSettingOptionsLoading"
        :role-options="roleOptions"
        :workspace-options="workspaceOptions"
      />
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submitBatchSetUserRoles">
        保存
      </el-button>
    </template>
  </MkDialog>
</template>
