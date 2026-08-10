<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import CommonApi from '@/api/admin/system/common'
import ChatUserApi from '@/api/admin/system/chat-user'
import ChatUserGroupsApi from '@/api/admin/system/chat-user-groups'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import type { ChatUser, ChatUserRequest } from '@/api/types'
import type { CascaderOption, CascaderProps, FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'UserFromDrawer' })

const { auth } = useStore()

const emit = defineEmits<{
  refresh: [resetQuery: boolean] //是否从第一页刷新
}>()

const userFormRef = ref<FormInstance>()
const drawerVisible = ref(false)
const isEdit = ref(false)
const editingUserId = ref('')
const userSubmitting = ref(false)
const userForm = reactive<ChatUserRequest>({
  email: '',
  nick_name: '',
  password: '',
  phone: '',
  user_group_ids: [],
  username: '',
})

const drawerTitle = computed(() => (isEdit.value ? '编辑用户' : '创建用户'))
const submitText = computed(() => (isEdit.value ? '保存' : '创建'))

const userFormRules = reactive<FormRules<ChatUserRequest>>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 64, message: '长度应为 4-64 个字符', trigger: 'blur' },
  ],
  nick_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 64, message: '长度应为 1-64 个字符', trigger: 'blur' },
  ],
  email: [{ type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
})

// 用户组选项
const userGroupOptions = ref<CascaderOption[]>([])
const userGroupCascaderProps: CascaderProps = {
  children: 'children',
  emitPath: false,
  label: 'name',
  multiple: true,
  value: 'id',
}

// 默认密码
function loadDefaultPassword() {
  return CommonApi.getDefaultPassword().then(({ password }) => {
    userForm.password = password
  })
}

async function copyDefaultPassword() {
  if (userForm.password) {
    await navigator.clipboard.writeText(userForm.password)
    MsgSuccess('默认密码已复制')
  }
}

function loadUserGroupOptions() {
  return ChatUserGroupsApi.getChatUserGroups().then((groups) => {
    userGroupOptions.value = groups
  })
}

async function submitUser() {
  if (!userFormRef.value) return
  await userFormRef.value.validate((valid) => {
    if (valid) {
      userSubmitting.value = true

      if (isEdit.value) {
        ChatUserApi.putChatUser(editingUserId.value, userForm)
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
        ChatUserApi.postChatUser({
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

function open(user?: ChatUser) {
  resetData()
  if (user) {
    Object.assign(userForm, {
      username: user.username,
      email: user.email ?? '',
      nick_name: user.nick_name,
      phone: user.phone ?? '',
      user_group_ids: [...user.user_group_ids],
    })
    editingUserId.value = user.id
    isEdit.value = true
  }
  loadUserGroupOptions()
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
    nick_name: '',
    password: '',
    phone: '',
    user_group_ids: [],
    username: '',
  })
  isEdit.value = false
  editingUserId.value = ''
  userSubmitting.value = false
  userGroupOptions.value = []
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
              <el-button text @click="copyDefaultPassword" class="-mr-1">
                <mk-icon name="icon_copy_outlined" class="text-N600"></mk-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </section>
      <section>
        <h4 class="mk-title-decoration mb-4 mt-4">用户组</h4>
        <el-form-item>
          <el-cascader
            v-model="userForm.user_group_ids"
            class="w-full"
            :options="userGroupOptions"
            :props="userGroupCascaderProps"
            :show-all-levels="false"
            clearable
            filterable
            placeholder="请选择用户组"
          />
        </el-form-item>
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
