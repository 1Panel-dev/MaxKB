<template>
  <div class="authentication-setting__main main-calc-height">
    <el-scrollbar>
      <div class="form-container p-24" v-loading="loading">
        <el-form
          ref="authFormRef"
          :model="form"
          label-position="top"
          require-asterisk-position="right"
          @submit.prevent
        >
          <!-- 登录方式选择框 -->
          <el-form-item
            :label="$t('views.system.default_login')"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.loginMethodRequired'),
                trigger: 'change',
              },
            ]"
            prop="default_value"
            style="padding-top: 16px"
          >
            <el-radio-group
              v-model="form.default_value"
              class="radio-group"
              style="margin-left: 10px"
            >
              <el-radio
                v-for="method in loginMethods"
                :key="method.value"
                :label="method.value"
                class="radio-item"
              >
                {{ method.label }}
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item
            :label="$t('views.system.display_code')"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.displayCodeRequired'),
                trigger: 'change',
              },
            ]"
            prop="max_attempts"
          >
            <el-row :gutter="16" style="margin-left: 10px">
              <el-col :span="24">
                <span style="font-size: 13px">
                  {{ $t('views.system.loginFailed') }}
                </span>
                <el-input-number
                  style="margin-left: 8px"
                  v-model="form.max_attempts"
                  :min="-1"
                  :max="10"
                  :step="1"
                  controls-position="right"
                  @change="onMaxAttemptsChange"
                />
                <span style="margin-left: 8px; font-size: 13px">
                  {{ $t('views.system.loginFailedMessage') }}
                </span>
                <span style="margin-left: 8px; color: #909399; font-size: 12px">
                  ({{ $t('views.system.display_codeTip') }})
                </span>
              </el-col>

              <el-col :span="24" style="margin-top: 8px">
                <span style="font-size: 13px">
                  {{ $t('views.system.loginFailed') }}
                </span>
                <el-input-number
                  style="margin-left: 8px"
                  v-model="form.failed_attempts"
                  :min="-1"
                  :max="10"
                  :step="1"
                  controls-position="right"
                  @change="onFailedAttemptsChange"
                />
                <span style="margin-left: 8px; font-size: 13px">
                  {{ $t('views.system.failedTip') }}
                </span>
                <el-input-number
                  style="margin-left: 8px"
                  v-model="form.lock_time"
                  :min="1"
                  :step="1"
                  controls-position="right"
                />
                <span style="margin-left: 8px; font-size: 13px">
                  {{ $t('views.system.minute') }}
                </span>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item
            :label="$t('views.system.third_party_user_default_role')"
            :rules="[
              {
                required: true,
                message: $t('views.system.thirdPartyUserDefaultRoleRequired'),
                trigger: 'change',
              },
            ]"
          >
            <el-row :gutter="16" style="margin-left: 10px">
              <el-col :span="24">
                <div class="flex">
                  <span
                    style="font-size: 13px; white-space: nowrap; width: 50px"
                    class="text-right mr-8"
                  >
                    {{ $t('views.role.member.role') }}
                  </span>
                  <el-select
                    filterable
                    clearable
                    v-model="form.role_id"
                    :placeholder="`${$t('common.selectPlaceholder')}${$t('views.role.member.role')}`"
                    @change="handleRoleChange"
                    class="w-240"
                  >
                    <el-option
                      v-for="role in roleOptions"
                      :key="role.id"
                      :label="role.name"
                      :value="role.id"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="24" v-if="user.isEE() && showWorkspaceSelector" class="mt-16">
                <div class="flex">
                  <span
                    style="font-size: 13px; white-space: nowrap; width: 50px"
                    class="text-right mr-8"
                  >
                    {{ $t('views.role.member.workspace') }}
                  </span>
                  <el-select
                    filterable
                    clearable
                    v-model="form.workspace_id"
                    :placeholder="`${$t('common.selectPlaceholder')}${$t('views.role.member.workspace')}`"
                    class="w-240"
                  >
                    <el-option
                      v-for="workspace in workspaceOptions"
                      :key="workspace.id"
                      :label="workspace.name"
                      :value="workspace.id"
                    />
                  </el-select>
                </div>
              </el-col>
              <el-col
                :span="24"
                v-if="(user.isEE() || user.isPE()) && showPermissionSelector"
                class="mt-16"
              >
                <div class="flex">
                  <span
                    style="font-size: 13px; white-space: nowrap; width: 50px"
                    class="text-right mr-8"
                  >
                    {{ $t('views.system.resourceAuthorization.title') }}
                  </span>
                  <el-select
                    filterable
                    clearable
                    v-model="form.permission"
                    :placeholder="`${$t('common.selectPlaceholder')}${$t('views.system.resourceAuthorization.title')}`"
                    class="w-240"
                  >
                    <el-option
                      v-for="permission in permissionOptions"
                      :key="permission.value"
                      :label="permission.label"
                      :value="permission.value"
                    />
                  </el-select>
                </div>
              </el-col>
            </el-row>
          </el-form-item>
        </el-form>
        <div style="margin-top: 16px">
          <span
            v-hasPermission="
              new ComplexPermission([RoleConst.ADMIN], [PermissionConst.LOGIN_AUTH_EDIT], [], 'OR')
            "
            class="mr-12"
          >
            <!-- 直接调用 submit，不传参 -->
            <el-button @click="submit" type="primary" :disabled="loading">
              {{ $t('common.save') }}
            </el-button>
          </span>
        </div>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ComplexPermission } from '@/utils/permission/type'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import type { FormInstance } from 'element-plus'
import { t } from '@/locales'
import authApi from '@/api/system-settings/auth-setting.ts'
import { MsgSuccess } from '@/utils/message.ts'
import WorkspaceApi from '@/api/workspace/workspace.ts'
import useStore from '@/stores'
import { AuthorizationEnum } from '@/enums/system.ts'
import { hasPermission } from '@/utils/permission'

const loginMethods = ref<Array<{ label: string; value: string }>>([])
const loading = ref(false)
// 明确允许 null，避免未挂载时访问出错
const authFormRef = ref<FormInstance | null>(null)

const form = ref<any>({
  default_value: 'LOCAL',
  max_attempts: 1,
  failed_attempts: 5,
  lock_time: 10,
  role_id: 'USER',
  workspace_id: 'default',
  permission: 'NOT_AUTH',
})

const normalizeInputValue = (val: number | null): number => {
  // 若输入为空或无法转换为有效数字，默认设为 1
  let normalizedVal = typeof val === 'number' ? Math.trunc(val) : NaN
  if (!Number.isFinite(normalizedVal)) {
    normalizedVal = 1
  }

  if (normalizedVal === 0) {
    normalizedVal = 1
  } else if (normalizedVal < -1) {
    normalizedVal = -1
  }

  return normalizedVal
}

const onFailedAttemptsChange = (val: number | null) => {
  form.value.failed_attempts = normalizeInputValue(val)
}

const onMaxAttemptsChange = (val: number | null) => {
  form.value.max_attempts = normalizeInputValue(val)
}

// 提交：使用 authFormRef.value.validate() 的 Promise 风格，并保证 loading 在 finally 中恢复
const submit = async () => {
  const formRef = authFormRef.value
  if (!formRef) return
  try {
    await formRef.validate()
    loading.value = true
    const params = {
      default_value: form.value.default_value,
      max_attempts: form.value.max_attempts,
      failed_attempts: form.value.failed_attempts,
      lock_time: form.value.lock_time,
      role_id: form.value.role_id,
      workspace_id: form.value.workspace_id,
      permission: form.value.permission,
    }
    await authApi.putLoginSetting(params)
    MsgSuccess(t('common.saveSuccess'))
  } catch (err) {
    // 验证或请求失败：按需处理，避免未捕获异常
    // console.error(err);
  } finally {
    loading.value = false
  }
}

const roleOptions = ref<Array<{ id: string; name: string; type?: string }>>([])
const workspaceOptions = ref<Array<{ id: string; name: string }>>([])
const { user } = useStore()
const selectedRoleType = ref<string>('') // 存储选中角色类型，用于控制 workspace 显示
const showWorkspaceSelector = computed(() => selectedRoleType.value !== 'ADMIN')
const showPermissionSelector = computed(() => selectedRoleType.value === 'USER')
const permissionOptions = computed(() => {
  const baseOptions = [
    {
      label: t('views.system.resourceAuthorization.setting.check'),
      value: AuthorizationEnum.VIEW,
      desc: t('views.system.resourceAuthorization.setting.checkDesc'),
    },
    {
      label: t('views.system.resourceAuthorization.setting.management'),
      value: AuthorizationEnum.MANAGE,
      desc: t('views.system.resourceAuthorization.setting.managementDesc'),
    },
    {
      label: t('views.system.resourceAuthorization.setting.notAuthorized'),
      value: AuthorizationEnum.NOT_AUTH,
      desc: '',
    },
  ]

  if (hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')) {
    baseOptions.splice(2, 0, {
      label: t('views.system.resourceAuthorization.setting.role'),
      value: AuthorizationEnum.ROLE,
      desc: t('views.system.resourceAuthorization.setting.roleDesc'),
    })
  }

  return baseOptions
})
// 当角色变更时更新 selectedRoleType
const handleRoleChange = (roleId: string) => {
  const selectedRole = roleOptions.value.find((role) => role.id === roleId)
  selectedRoleType.value = selectedRole?.type || ''
  if (form.value.workspace_id === 'None' && showWorkspaceSelector) {
    form.value.workspace_id = 'default'
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const isEE = typeof user?.isEE === 'function' ? user.isEE() : false

    // 并行请求：角色列表 + 登录设置；若为 EE 同时请求 workspace 列表
    const roleP = WorkspaceApi.getWorkspaceRoleList()
      .then((r) => r)
      .catch(() => ({ data: [] }))
    const settingP = authApi
      .getLoginSetting()
      .then((r) => r)
      .catch(() => ({ data: {} }))
    const tasks: Promise<any>[] = [roleP, settingP]
    if (isEE) {
      tasks.push(
        WorkspaceApi.getWorkspaceList()
          .then((r) => r)
          .catch(() => ({ data: [] })),
      )
    }

    const results = await Promise.all(tasks)
    const roleRes = results[0] ?? { data: [] }
    const settingRes = results[1] ?? { data: {} }
    const workspaceRes = isEE ? (results[2] ?? { data: [] }) : null

    // 处理角色列表（尽早回显）
    const rolesData = Array.isArray(roleRes?.data) ? roleRes.data : []
    roleOptions.value = rolesData.map((item: any) => ({
      id: item.id,
      name: item.name,
      type: item.type,
    }))

    // 处理 setting（合并默认值，避免访问未定义）
    const data = settingRes?.data ?? {}
    form.value = {
      ...form.value,
      ...data,
      failed_attempts: data.failed_attempts ?? form.value.failed_attempts ?? 5,
      lock_time: data.lock_time ?? form.value.lock_time ?? 10,
      role_id: data.role_id ?? form.value.role_id ?? 'USER',
      workspace_id: data.workspace_id ?? form.value.workspace_id ?? 'default',
      permission: data.permission ?? form.value.permission ?? 'NOT_AUTH',
    }
    loginMethods.value = Array.isArray(data.auth_types) ? data.auth_types : []

    // 处理 workspace 列表（如果需要）
    if (isEE && workspaceRes) {
      const wks = Array.isArray(workspaceRes.data) ? workspaceRes.data : []
      workspaceOptions.value = wks.map((item: any) => ({ id: item.id, name: item.name }))
    }

    // 初始化 selectedRoleType（基于当前回显的 role_id 与已加载的 roleOptions）
    const initRole = roleOptions.value.find((r) => r.id === form.value.role_id)
    selectedRoleType.value = initRole?.type || ''
  } catch (e) {
    // overall error, 保持默认回显
    // console.error(e);
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.radio-group {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
}
</style>
