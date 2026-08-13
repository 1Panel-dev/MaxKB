<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import AuthSettingApi from '@/api/admin/system/auth-setting'
import UserGroupsApi from '@/api/admin/system/user-groups'
import {
  LOGIN_METHOD,
  ROLE_TYPE,
  type ListItem,
  type LoginAuthSetting,
  type SystemUserGroup,
  type LoginMethod,
} from '@/api/types'
import { LOGIN_METHOD_LABELS } from '@/constants/auth'
import { MsgSuccess } from '@/utils/message'
import { useStore } from '@/stores'

defineOptions({ name: 'AuthenticationSetting' })
const { auth } = useStore()
const authFormRef = useTemplateRef<FormInstance>('authFormRef')
const loading = ref(false)
const form = reactive<LoginAuthSetting>({
  login_methods: [LOGIN_METHOD.LOCAL],
  default_value: LOGIN_METHOD.LOCAL,
  max_attempts: 1,
  failed_attempts: 5,
  lock_time: 10,
  role_id: ROLE_TYPE.USER,
  workspace_id: 'default',
  permission: 'NOT_AUTH',
})
const rules: FormRules<LoginAuthSetting> = {
  default_value: [{ required: true, message: '请选择默认登录方式', trigger: 'change' }],
  login_methods: [{ required: true, message: '请选择登录方式', trigger: 'change' }],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }],
  workspace_id: [{ required: true, message: '请选择工作空间', trigger: 'change' }],
}

/* 登录方式加载与提交 */
const loginMethodOptions = computed(() => form.login_methods)
const defaultLoginMethodOptions = computed(() => form.auth_types)
function loadSetting() {
  loading.value = true
  return AuthSettingApi.getLoginSetting()
    .then((setting) => {
      Object.assign(form, setting)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleLoginMethodsChange(loginMethods: string[]) {
  if (!loginMethods.includes(form.default_value)) {
    form.default_value = loginMethods[0] ?? ''
  }
}

/* 登录次数不为0*/
function normalizeNonZeroNumber(value: number | undefined) {
  return value === undefined || value === 0 ? 1 : value
}

// 角色与工作空间选项
const roleSettingOptionsLoading = ref(false)
const roleOptions = ref<ListItem[]>([])
const workspaceOptions = ref<ListItem[]>([])
const selectedRoleType = computed(
  () => roleOptions.value.find(({ id }) => id === form.role_id)?.type,
)
const showWorkspaceSelector = computed(() => selectedRoleType.value !== ROLE_TYPE.ADMIN)

function loadRoleSettingOptions() {
  roleSettingOptionsLoading.value = true
  const roleSettingOptionRequests: Promise<void>[] = []

  roleSettingOptionRequests.push(
    CurrentUserApi.getCurrentUserRoleList().then((roles) => {
      roleOptions.value = roles
    }),
  )
  if (auth.isEE) {
    roleSettingOptionRequests.push(
      CurrentUserApi.getCurrentUserWorkspaceList().then((workspaces) => {
        workspaceOptions.value = workspaces
      }),
    )
  }

  return Promise.all(roleSettingOptionRequests).finally(() => {
    roleSettingOptionsLoading.value = false
  })
}

function handleRoleChange() {
  if (!showWorkspaceSelector.value) {
    form.workspace_id = undefined
    form.group_id = undefined
    userGroups.value = []
  }
}

function handleWorkspaceChange() {
  form.group_id = undefined
  loadUserGroups()
}

/* 选择用户组列表 */
const loadingGroups = ref(false)
const userGroups = ref<SystemUserGroup[]>([])

function loadUserGroups() {
  if (!form.workspace_id || !showWorkspaceSelector.value) {
    userGroups.value = []
    form.group_id = undefined
    return Promise.resolve()
  }

  loadingGroups.value = true
  return UserGroupsApi.getSystemUserGroups(form.workspace_id)
    .then((groups) => {
      userGroups.value = groups
      if (!groups.some(({ id }) => id === form.group_id)) {
        form.group_id = undefined
      }
    })
    .finally(() => {
      loadingGroups.value = false
    })
}

function submit() {
  authFormRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    AuthSettingApi.putLoginSetting(form)
      .then(() => MsgSuccess('保存成功'))
      .finally(() => {
        loading.value = false
      })
  })
}

onMounted(() => {
  Promise.all([loadSetting(), loadRoleSettingOptions()]).then(() => {
    return loadUserGroups()
  })
})
</script>

<template>
  <el-form
    v-loading="loading"
    ref="authFormRef"
    class="max-w-200"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
  >
    <el-form-item label="登录方式" prop="login_methods">
      <el-checkbox-group v-model="form.login_methods" @change="handleLoginMethodsChange">
        <el-checkbox
          v-for="loginMethodOption in loginMethodOptions"
          :key="loginMethodOption"
          :value="loginMethodOption"
          class="w-40"
        >
          {{ LOGIN_METHOD_LABELS[loginMethodOption as LoginMethod] }}
        </el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="默认登录方式" prop="default_value">
      <el-select v-model="form.default_value">
        <el-option
          v-for="loginMethodOption in defaultLoginMethodOptions"
          :key="loginMethodOption.value"
          :value="loginMethodOption.value"
          :label="loginMethodOption.label"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="账号登录验证码设置" required>
      <el-card shadow="never" class="bg-N100! w-full">
        <div class="flex items-center gap-2">
          <span>登录失败</span>
          <el-input-number
            v-model="form.max_attempts"
            :max="10"
            :min="-1"
            :step="1"
            :value-on-clear="-1"
            @change="form.max_attempts = normalizeNonZeroNumber($event)"
          />
          <span>登录失败</span>
          <span class="text-N500">(值为-1时，不显示验证码)</span>
        </div>
        <div class="flex items-center gap-2 mt-4">
          <span>登录失败</span>
          <el-input-number
            v-model="form.failed_attempts"
            :max="10"
            :min="-1"
            :step="1"
            :value-on-clear="-1"
            @change="form.max_attempts = normalizeNonZeroNumber($event)"
          />
          <span>次，</span>
          <span>锁定账号</span>
          <el-input-number
            v-model="form.lock_time"
            :min="1"
            :step="1"
            :value-on-clear="1"
            @change="form.max_attempts = normalizeNonZeroNumber($event)"
          />
          <span>分钟</span>
        </div>
      </el-card>
    </el-form-item>
    <p class="mb-2">第三方用户默认角色分配</p>
    <el-card shadow="never" class="bg-N100!">
      <el-form-item label="角色" prop="role_id">
        <el-select
          v-model="form.role_id"
          :loading="roleSettingOptionsLoading"
          filterable
          clearable
          placeholder="请选择角色"
          @change="handleRoleChange"
        >
          <el-option
            v-for="role in roleOptions"
            :key="role.id"
            :label="role.name"
            :value="role.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="工作空间" prop="workspace_id" v-if="auth.isEE && showWorkspaceSelector">
        <el-select
          v-model="form.workspace_id"
          :loading="roleSettingOptionsLoading"
          filterable
          clearable
          placeholder="请选择工作空间"
          @change="handleWorkspaceChange"
        >
          <el-option
            v-for="workspace in workspaceOptions"
            :key="workspace.id"
            :label="workspace.name"
            :value="workspace.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="用户组" v-if="form.workspace_id">
        <el-select
          filterable
          clearable
          v-model="form.group_id"
          :loading="loadingGroups"
          placeholder="请选择用户组"
          class="w-240"
        >
          <el-option
            v-for="userGroup in userGroups"
            :key="userGroup.id"
            :label="userGroup.name"
            :value="userGroup.id"
          />
        </el-select>
      </el-form-item>
    </el-card>
    <el-button class="mt-4" type="primary" @click="submit">保存</el-button>
  </el-form>
</template>
