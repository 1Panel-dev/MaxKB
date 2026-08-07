<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import CurrentUserApi from '@/api/admin/auth/current-user'
import { useStore } from '@/stores'
import type { WorkspaceItem, List } from '@/types'
import { Delete, Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'UserFromDrawer' })

const { auth } = useStore()

const drawerVisible = ref(false)
const isEdit = ref(false)
const userFormRef = ref<FormInstance>()
const userForm = reactive({
  email: '',
  nick_name: '',
  password: '',
  phone: '',
  role_setting: [{ role_id: '', workspace_ids: [] as string[] }],
  username: '',
})

const drawerTitle = computed(() => (isEdit.value ? '编辑用户' : '创建用户'))
const submitText = computed(() => (isEdit.value ? '保存' : '创建'))

const userFormRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 64, message: '长度应为 4-64 个字符', trigger: 'blur' },
  ],
  nick_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 64, message: '长度应为 1-64 个字符', trigger: 'blur' },
  ],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],

  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
})

function open(data?: unknown) {
  nextTick(() => userFormRef.value?.clearValidate())
  isEdit.value = Boolean(data)
  drawerVisible.value = true
  if (auth.isEE || auth.isPE) {
    loadRoleSettingOptions()
  }
}

function close() {
  drawerVisible.value = false
}

// 角色设置选项
const roleSettingOptionsLoading = ref(false)
const roleOptions = ref<List[]>([])
const workspaceOptions = ref<WorkspaceItem[]>([])

function loadRoleSettingOptions() {
  roleSettingOptionsLoading.value = true

  return Promise.all([
    CurrentUserApi.getCurrentUserRoleList(),
    CurrentUserApi.getCurrentUserWorkspaceList(),
  ])
    .then(([roles, workspaces]) => {
      roleOptions.value = roles
      workspaceOptions.value = workspaces
    })
    .finally(() => {
      roleSettingOptionsLoading.value = false
    })
}

function addRole() {
  userForm.role_setting.push({ role_id: '', workspace_ids: [] })
}

function removeRole(index: number) {
  if (userForm.role_setting.length === 1) return
  userForm.role_setting.splice(index, 1)
}

async function copyDefaultPassword() {
  await navigator.clipboard.writeText(userForm.password)
  MsgSuccess('默认密码已复制')
}

async function submitUser() {
  const valid = await userFormRef.value?.validate().catch(() => false)
  if (!valid) return
}

defineExpose({ close, open })
</script>

<template>
  <el-drawer
    v-model="drawerVisible"
    direction="rtl"
    size="600"
    :show-close="true"
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header>
      <h4>{{ drawerTitle }}</h4>
    </template>
    <el-scrollbar>
      <div class="p-5">
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
                  <el-button text @click="copyDefaultPassword" class="-mr-1">
                    <mk-icon name="icon_copy_outlined" class="text-N600"></mk-icon>
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </section>

          <section v-if="auth.isEE || auth.isPE" v-loading="roleSettingOptionsLoading">
            <h4 class="mk-title-decoration mb-4">角色设置</h4>

            <div
              v-for="(roleAssignment, index) in userForm.role_setting"
              :key="index"
              class="flex items-center w-full gap-2"
            >
              <el-form-item label="角色" required class="flex-1">
                <el-select v-model="roleAssignment.role_id" placeholder="请选择角色">
                  <el-option
                    v-for="roleOption in roleOptions"
                    :key="roleOption.id"
                    :label="roleOption.name"
                    :value="roleOption.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="工作空间" required class="flex-1">
                <el-select
                  v-model="roleAssignment.workspace_ids"
                  multiple
                  placeholder="请选择工作空间"
                >
                  <el-option
                    v-for="workspaceOption in workspaceOptions"
                    :key="workspaceOption.id"
                    :label="workspaceOption.name"
                    :value="workspaceOption.id"
                  />
                </el-select>
              </el-form-item>

              <el-button
                :disabled="userForm.role_setting.length === 1"
                :icon="Delete"
                text
                @click="removeRole(index)"
              />
            </div>

            <el-button :icon="Plus" link type="primary" @click="addRole">添加角色</el-button>
          </section>
        </el-form>
      </div>
    </el-scrollbar>

    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="submitUser">
          {{ submitText }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<style lang="scss" scoped></style>
