<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserManageApi from '@/api/admin/system/user-manage'
import { ROLE_TYPE } from '@/api/enums'
import type {
  ListItem,
  BatchSetUserWorkspaceRolesRequest,
  SystemUserRoleAssignment,
} from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import MkFormList from '@/components/mk-form-list/index.vue'

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

function isAdminRole(roleId: string) {
  return roleOptions.value.find(({ id }) => id === roleId)?.type === ROLE_TYPE.ADMIN
}

function handleRoleChange(roleAssignment: SystemUserRoleAssignment, index: number) {
  if (isAdminRole(roleAssignment.role_id)) {
    roleAssignment.workspace_ids = []
    nextTick(() => batchRoleFormRef.value?.clearValidate(`role_setting.${index}.workspace_ids`))
  }
}

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
              roleOptions.value.find(({ id }) => id === assignment.role_id)?.type ===
              ROLE_TYPE.ADMIN
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
        dialogVisible.value = false
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

      <MkFormList
        v-if="auth.isEE || auth.isPE"
        v-model="batchRoleForm.role_setting"
        add-text="添加角色"
        :default-item="{ role_id: '', workspace_ids: [] }"
      >
        <template #default="{ index, item: roleAssignment }">
          <el-form-item
            class="flex-1"
            :label="index === 0 ? '角色' : ''"
            :prop="`role_setting.${index}.role_id`"
            :rules="{
              required: true,
              message: '请选择角色',
              trigger: 'change',
            }"
          >
            <el-select
              v-model="roleAssignment.role_id"
              placeholder="请选择角色"
              :loading="roleSettingOptionsLoading"
              clearable
              filterable
              fit-input-width
              @change="handleRoleChange(roleAssignment, index)"
            >
              <el-option
                v-for="roleOption in roleOptions"
                :key="roleOption.id"
                :label="roleOption.name"
                :title="roleOption.name"
                :value="roleOption.id"
              />
            </el-select>
          </el-form-item>

          <!-- 企业版用户的非系统管理员角色需要指定工作空间。 -->
          <el-form-item
            v-if="auth.isEE"
            class="flex-1"
            :label="index === 0 ? '工作空间' : ''"
            :prop="`role_setting.${index}.workspace_ids`"
            :rules="{
              required: !isAdminRole(roleAssignment.role_id),
              type: 'array',
              min: 1,
              message: '请选择工作空间',
              trigger: 'change',
            }"
          >
            <el-select
              v-model="roleAssignment.workspace_ids"
              :placeholder="isAdminRole(roleAssignment.role_id) ? '' : '请选择工作空间'"
              :loading="roleSettingOptionsLoading"
              :disabled="isAdminRole(roleAssignment.role_id)"
              :validate-event="!isAdminRole(roleAssignment.role_id)"
              clearable
              filterable
              fit-input-width
              multiple
              collapse-tags
              collapse-tags-tooltip
              :reserve-keyword="false"
            >
              <el-option
                v-for="workspaceOption in workspaceOptions"
                :key="workspaceOption.id"
                :label="workspaceOption.name"
                :title="workspaceOption.name"
                :value="workspaceOption.id"
              />
            </el-select>
          </el-form-item>
        </template>
      </MkFormList>
    </el-form>

    <template #footer>
      <el-button plain @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submitBatchSetUserRoles">
        保存
      </el-button>
    </template>
  </MkDialog>
</template>
