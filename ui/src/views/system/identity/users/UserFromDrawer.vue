<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import CommonApi from '@/api/admin/system/common'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserManageApi from '@/api/admin/system/user-manage'
import { useStore } from '@/stores'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import UserGroupSetting from './components/UserGroupSetting.vue'
import UserRoleSetting from './components/UserRoleSetting.vue'
import type {
  ListItem,
  SystemUser,
  SystemUserRequest,
  SystemUserRoleAssignment,
} from '@/api/types/index.ts'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'UserFromDrawer' })

const { auth } = useStore()

const emit = defineEmits<{
  refresh: [resetQuery: boolean] //是否从第一页刷新
}>()

const userFormRef = ref<FormInstance>()
const drawerVisible = ref(false)
const isEdit = ref(false)
const userSubmitting = ref(false)
const userForm = reactive<SystemUserRequest>({
  email: '',
  nick_name: '',
  password: '',
  phone: '',
  role_setting: [{ role_id: '', workspace_ids: [] }],
  username: '',
  user_group_ids: [],
})

const drawerTitle = computed(() => (isEdit.value ? '编辑用户' : '创建用户'))
const submitText = computed(() => (isEdit.value ? '保存' : '创建'))

const userFormRules = reactive<FormRules<SystemUserRequest>>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 64, message: '长度应为 4-64 个字符', trigger: 'blur' },
  ],
  nick_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 64, message: '长度应为 1-64 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' },
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
})

// 角色与工作空间选项
const roleSettingOptionsLoading = ref(false)
const roleOptions = ref<ListItem[]>([])
const workspaceOptions = ref<ListItem[]>([])

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

// 用户组相关
const selectedWorkspaceIds = computed(() => [
  ...new Set(userForm.role_setting.flatMap(({ workspace_ids }) => workspace_ids)),
])

// 默认密码
function loadDefaultPassword() {
  return CommonApi.getDefaultPassword().then(({ password }) => {
    userForm.password = password
  })
}

async function submitUser() {
  if (!userFormRef.value) return
  await userFormRef.value.validate((valid) => {
    if (valid) {
      userSubmitting.value = true

      if (isEdit.value) {
        UserManageApi.putUser(userForm.id as string, userForm)
          .then(() => {
            MsgSuccess('编辑成功')
            emit('refresh', false)
            close()
          })
          .finally(() => {
            userSubmitting.value = false
          })
      } else {
        const encryptor = new JSEncrypt()
        encryptor.setPublicKey(auth.baseProfile?.rsa ?? '')
        const encryptedPassword = encryptor.encrypt(userForm.password as string)
        UserManageApi.postUser({
          ...userForm,
          encrypted: true,
          password: encryptedPassword as string,
        })
          .then(() => {
            MsgSuccess('创建成功')
            emit('refresh', true)
            close()
          })
          .finally(() => {
            userSubmitting.value = false
          })
      }
    }
  })
}

function open(user?: SystemUser) {
  resetData()
  if (user) {
    Object.assign(userForm, {
      id: user.id,
      username: user.username,
      email: user.email,
      nick_name: user.nick_name,
      phone: user.phone,
      role_setting: user.role_setting?.length
        ? user.role_setting.map((item: SystemUserRoleAssignment) => ({
            ...item,
            workspace_ids: item.workspace_ids.includes('None') ? [] : item.workspace_ids,
          }))
        : [{ role_id: '', workspace_ids: [] }],
      user_group_ids: user.user_group_ids ?? [],
    })
    isEdit.value = true
  }
  if (auth.isEE || auth.isPE) {
    loadRoleSettingOptions()
  }
  if (!isEdit.value) {
    loadDefaultPassword()
  }
  drawerVisible.value = true
}

function close() {
  drawerVisible.value = false
  resetData()
}

function resetData() {
  Object.assign(userForm, {
    email: '',
    id: undefined,
    nick_name: '',
    password: '',
    phone: '',
    role_setting: [{ role_id: '', workspace_ids: [] }],
    user_group_ids: [],
    username: '',
  })
  isEdit.value = false
  roleSettingOptionsLoading.value = false
  userSubmitting.value = false
  roleOptions.value = []
  workspaceOptions.value = []
  userFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="drawerVisible" @closed="resetData">
    <template #header>
      <h4>{{ drawerTitle }}</h4>
    </template>
    <el-form
      ref="userFormRef"
      :model="userForm"
      :rules="userFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitUser"
    >
      <section>
        <h4 class="mk-title-decoration mb-4">基本信息</h4>
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            :disabled="isEdit"
            maxlength="64"
            minlength="4"
            placeholder="请输入用户名"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="姓名" prop="nick_name">
          <el-input
            v-model="userForm.nick_name"
            maxlength="64"
            placeholder="请输入姓名"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" type="email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" maxlength="11" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item v-if="!isEdit" label="默认密码">
          <el-input v-model="userForm.password" readonly>
            <template #suffix>
              <el-button text @click="copyText(userForm.password)" class="-mr-1">
                <mk-icon name="icon_copy_outlined" class="text-N600"></mk-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </section>
      <section v-if="auth.isEE || auth.isPE">
        <h4 class="mk-title-decoration mb-4 mt-4">角色设置</h4>
        <UserRoleSetting
          v-model="userForm.role_setting"
          :loading="roleSettingOptionsLoading"
          :role-options="roleOptions"
          :workspace-options="workspaceOptions"
        />
      </section>
      <section v-if="selectedWorkspaceIds.length">
        <h4 class="mk-title-decoration mb-4 mt-4">用户组</h4>
        <UserGroupSetting
          v-model="userForm.user_group_ids"
          :workspace-ids="selectedWorkspaceIds"
          :workspace-options="workspaceOptions"
        />
      </section>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button :loading="userSubmitting" type="primary" @click="submitUser">
        {{ submitText }}
      </el-button>
    </template>
  </MkDrawer>
</template>
