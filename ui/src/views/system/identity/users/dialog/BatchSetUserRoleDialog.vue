<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserManageApi from '@/api/admin/system/user-manage'
import type { ListItem, SystemUserRoleAssignment } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import UserRoleSetting from '../components/UserRoleSetting.vue'

defineOptions({ name: 'BatchSetUserRoleDialog' })

const { auth } = useStore()

const emit = defineEmits<{
  refresh: []
}>()

interface BatchSetUserRoleForm {
  ids: string[]
  is_append: boolean
  role_ids: string[]
  role_setting: SystemUserRoleAssignment[]
}

const defaultRoleAssignment = (): SystemUserRoleAssignment => ({
  role_id: '',
  workspace_ids: [],
})
const batchRoleFormRef = ref<FormInstance>()
const dialogVisible = ref(false)
const optionsLoading = ref(false)
const submitting = ref(false)
const roleOptions = ref<ListItem[]>([])
const workspaceOptions = ref<ListItem[]>([])
const batchRoleForm = reactive<BatchSetUserRoleForm>({
  ids: [],
  is_append: true,
  role_ids: [],
  role_setting: [defaultRoleAssignment()],
})
const batchRoleFormRules = reactive<FormRules<BatchSetUserRoleForm>>({
  role_ids: [{ required: true, type: 'array', min: 1, message: '请选择角色', trigger: 'change' }],
})

/* 角色与工作空间选项 */
function loadRoleSettingOptions() {
  optionsLoading.value = true
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
    optionsLoading.value = false
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
          role_ids: batchRoleForm.role_ids,
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
  resetData()
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
    role_ids: [],
    role_setting: [defaultRoleAssignment()],
  })
  optionsLoading.value = false
  submitting.value = false
  roleOptions.value = []
  workspaceOptions.value = []
  batchRoleFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="设置角色" @closed="resetData">
    <el-form
      ref="batchRoleFormRef"
      :model="batchRoleForm"
      :rules="batchRoleFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitBatchSetUserRoles"
    >
      <el-form-item label="设置方式" prop="is_append">
        <el-radio-group v-model="batchRoleForm.is_append">
          <el-radio :value="true">追加</el-radio>
          <el-radio :value="false">替换</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item v-if="auth.isPE" label="角色" prop="role_ids">
        <el-select
          v-model="batchRoleForm.role_ids"
          placeholder="请选择角色"
          :loading="optionsLoading"
          clearable
          filterable
          multiple
          collapse-tags
          collapse-tags-tooltip
        >
          <el-option
            v-for="roleOption in roleOptions"
            :key="roleOption.id"
            :label="roleOption.name"
            :value="roleOption.id"
          />
        </el-select>
      </el-form-item>

      <UserRoleSetting
        v-else-if="auth.isEE"
        v-model="batchRoleForm.role_setting"
        :loading="optionsLoading"
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
