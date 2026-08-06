<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import { CopyDocument, Delete, Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'UserFromDrawer' })

interface UserRoleAssignment {
  roleId: string
  workspaceId: string
}

interface UserFormValue {
  email: string
  nickName: string
  password: string
  phone: string
  roles: UserRoleAssignment[]
  username: string
}

interface UserSelectOption {
  label: string
  value: string
}

interface UserFormDrawerData extends Partial<Omit<UserFormValue, 'roles'>> {
  roles?: UserRoleAssignment[]
}

const props = withDefaults(
  defineProps<{
    roleOptions?: UserSelectOption[]
    workspaceOptions?: UserSelectOption[]
  }>(),
  {
    roleOptions: () => [],
    workspaceOptions: () => [],
  },
)

const emit = defineEmits<{
  submit: [userForm: UserFormValue]
}>()

const DEFAULT_PASSWORD = 'MaxKB@123'

function createEmptyForm(): UserFormValue {
  return {
    email: '',
    nickName: '',
    password: DEFAULT_PASSWORD,
    phone: '',
    roles: [{ roleId: '', workspaceId: '' }],
    username: '',
  }
}

const drawerVisible = ref(false)
const isEdit = ref(false)
const userFormRef = ref<FormInstance>()
const userForm = reactive<UserFormValue>(createEmptyForm())

const drawerTitle = computed(() => (isEdit.value ? '编辑用户' : '创建用户'))
const submitText = computed(() => (isEdit.value ? '保存' : '创建'))
const submitDisabled = computed(
  () =>
    !userForm.nickName.trim() ||
    !userForm.username.trim() ||
    userForm.roles.some(({ roleId, workspaceId }) => !roleId || !workspaceId),
)

const userFormRules: FormRules<UserFormValue> = {
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }],
  nickName: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { max: 64, message: '姓名不能超过 64 个字符', trigger: 'blur' },
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 20, message: '用户名长度应为 4-20 个字符', trigger: 'blur' },
  ],
}

function resetForm(data?: UserFormDrawerData) {
  Object.assign(userForm, createEmptyForm(), data)
  userForm.roles = data?.roles?.length
    ? data.roles.map((role) => ({ ...role }))
    : [{ roleId: '', workspaceId: '' }]
}

function open(data?: UserFormDrawerData) {
  isEdit.value = Boolean(data)
  resetForm(data)
  drawerVisible.value = true
  nextTick(() => userFormRef.value?.clearValidate())
}

function close() {
  drawerVisible.value = false
}

function addRole() {
  userForm.roles.push({ roleId: '', workspaceId: '' })
}

function removeRole(index: number) {
  if (userForm.roles.length === 1) return
  userForm.roles.splice(index, 1)
}

async function copyDefaultPassword() {
  await navigator.clipboard.writeText(userForm.password)
  MsgSuccess('默认密码已复制')
}

async function submitUser() {
  const valid = await userFormRef.value?.validate().catch(() => false)
  if (!valid || submitDisabled.value) return

  emit('submit', {
    ...userForm,
    email: userForm.email.trim(),
    nickName: userForm.nickName.trim(),
    phone: userForm.phone.trim(),
    roles: userForm.roles.map((role) => ({ ...role })),
    username: userForm.username.trim(),
  })
}

defineExpose({ close, open })
</script>

<template>
  <el-drawer
    v-model="drawerVisible"
    class="user-form-drawer"
    direction="rtl"
    size="600px"
    :show-close="true"
  >
    <template #header>
      <h3>{{ drawerTitle }}</h3>
    </template>

    <el-scrollbar>
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent="submitUser"
      >
        <section>
          <h4 class="section-title">基本信息</h4>

          <el-form-item label="姓名" prop="nickName">
            <el-input
              v-model="userForm.nickName"
              maxlength="64"
              placeholder="请输入姓名"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="userForm.username"
              :disabled="isEdit"
              maxlength="20"
              placeholder="请输入用户名"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userForm.email" placeholder="请输入邮箱" />
          </el-form-item>

          <el-form-item label="手机号" prop="phone">
            <el-input v-model="userForm.phone" maxlength="11" placeholder="请输入手机号" />
          </el-form-item>

          <el-form-item v-if="!isEdit" label="默认密码">
            <el-input v-model="userForm.password" readonly>
              <template #suffix>
                <el-button
                  aria-label="复制默认密码"
                  :icon="CopyDocument"
                  text
                  @click="copyDefaultPassword"
                />
              </template>
            </el-input>
          </el-form-item>
        </section>

        <section class="mt-8">
          <h4 class="section-title">角色设置</h4>

          <div
            v-for="(roleAssignment, index) in userForm.roles"
            :key="index"
            class="mb-3 grid grid-cols-[1fr_1fr_32px] items-end gap-2"
          >
            <el-form-item class="!mb-0" label="角色" required>
              <el-select v-model="roleAssignment.roleId" placeholder="请选择角色">
                <el-option
                  v-for="roleOption in props.roleOptions"
                  :key="roleOption.value"
                  :label="roleOption.label"
                  :value="roleOption.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item class="!mb-0" label="工作空间" required>
              <el-select v-model="roleAssignment.workspaceId" placeholder="请选择工作空间">
                <el-option
                  v-for="workspaceOption in props.workspaceOptions"
                  :key="workspaceOption.value"
                  :label="workspaceOption.label"
                  :value="workspaceOption.value"
                />
              </el-select>
            </el-form-item>

            <el-button
              aria-label="删除角色"
              class="mb-0.5"
              :disabled="userForm.roles.length === 1"
              :icon="Delete"
              text
              @click="removeRole(index)"
            />
          </div>

          <el-button :icon="Plus" link type="primary" @click="addRole">添加角色</el-button>
        </section>
      </el-form>
    </el-scrollbar>

    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="close">取消</el-button>
        <el-button :disabled="submitDisabled" type="primary" @click="submitUser">
          {{ submitText }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<style lang="scss" scoped>
.section-title {
  border-left: 3px solid var(--mk-primary);
  margin-bottom: calc(var(--spacing) * 5);
  padding-left: calc(var(--spacing) * 2);
}

:global(.user-form-drawer .el-drawer__body) {
  overflow: hidden;
  padding: calc(var(--spacing) * 7) calc(var(--spacing) * 6);
}

:global(.user-form-drawer .el-drawer__footer),
:global(.user-form-drawer .el-drawer__header) {
  margin-bottom: 0;
  padding: calc(var(--spacing) * 5) calc(var(--spacing) * 6);
}

:global(.user-form-drawer .el-drawer__footer) {
  border-top: 1px solid var(--el-border-color-lighter);
}

:global(.user-form-drawer .el-drawer__header) {
  border-bottom: 1px solid var(--el-border-color-lighter);
}

:global(.user-form-drawer .el-form-item) {
  margin-bottom: calc(var(--spacing) * 5);
}

:global(.user-form-drawer .el-select) {
  width: 100%;
}
</style>
