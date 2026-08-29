<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import CommonSystemApi from '@/api/admin/system/common'
import ChatUserApi from '@/api/admin/system/chat-user/chat-user'
import ChatUserGroupsApi from '@/api/admin/system/chat-user/chat-user-groups'
import { useStore } from '@/stores'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import type { ListItem, ChatUser, ChatUserPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'

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
const userForm = reactive<ChatUserPayload>({
  email: '',
  nick_name: '',
  password: '',
  phone: '',
  user_group_ids: [],
  username: '',
})

const drawerTitle = computed(() => (isEdit.value ? '编辑用户' : '创建用户'))
const submitText = computed(() => (isEdit.value ? '保存' : '创建'))

const userFormRules = reactive<FormRules<ChatUserPayload>>({
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
  user_group_ids: [
    {
      type: 'array',
      required: true,
      message: '请选择用户组',
      trigger: 'change',
    },
  ],
})

/* 用户组选项 */
const userGroupOptions = ref<ListItem[]>([])
const userGroupOptionsLoading = ref(false)

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

// 默认密码
function loadDefaultPassword() {
  return CommonSystemApi.getDefaultPassword().then(({ password }) => {
    userForm.password = password
  })
}

async function submitUser() {
  if (!userFormRef.value) return
  await userFormRef.value.validate((valid) => {
    if (valid) {
      userSubmitting.value = true

      if (isEdit.value) {
        ChatUserApi.putChatUser(editingUserId.value, {
          email: userForm.email,
          nick_name: userForm.nick_name,
          phone: userForm.phone,
          user_group_ids: userForm.user_group_ids,
        })
          .then(() => {
            MsgSuccess('编辑成功')
            emit('refresh', false)
            drawerVisible.value = false
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
            drawerVisible.value = false
          })
          .finally(() => {
            userSubmitting.value = false
          })
      }
    }
  })
}

function open(user?: ChatUser) {
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
  userGroupOptionsLoading.value = false
  userGroupOptions.value = []
  userFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="drawerVisible" :title="drawerTitle" @closed="resetData">
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
      <section>
        <h4 class="mk-title-decoration mb-4 mt-4">用户组</h4>
        <el-form-item label="用户组" prop="user_group_ids">
          <el-select
            v-model="userForm.user_group_ids"
            class="w-full"
            :loading="userGroupOptionsLoading"
            clearable
            filterable
            multiple
            placeholder="请选择用户组"
            fit-input-width
          >
            <el-option
              v-for="userGroup in userGroupOptions"
              :key="userGroup.id"
              :label="userGroup.name"
              :value="userGroup.id"
            />
          </el-select>
        </el-form-item>
      </section>
    </el-form>

    <template #footer>
      <el-button plain @click="drawerVisible = false">取消</el-button>
      <el-button :loading="userSubmitting" type="primary" @click="submitUser">
        {{ submitText }}
      </el-button>
    </template>
  </MkDrawer>
</template>
