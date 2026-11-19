<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import JSEncrypt from 'jsencrypt'
import { useI18n } from 'vue-i18n'
import type { ChatUser, ChatUserPayload, ListItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import ChatUserApi from '@/api/admin/system/chat-management/chat-user'
import ChatUserGroupsApi from '@/api/admin/system/chat-management/chat-user-groups'
import CommonSystemApi from '@/api/admin/system/common'
import { useStore } from '@/stores'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'UserFromDrawer' })

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

const emit = defineEmits<{
  refresh: [resetQuery: boolean] //是否从第一页刷新
}>()

const userFormRef = ref<FormInstance>()
const drawerVisible = ref(false)
const isEdit = ref(false)
const editingUserId = ref('')
const userSubmitting = ref(false)
const userForm = reactive<ChatUserPayload>({ email: '', nick_name: '', password: '', phone: '', user_group_ids: [], username: '' })

const drawerTitle = computed(() => t(isEdit.value ? 'user.editTitle' : 'user.createTitle'))
const submitText = computed(() => t(isEdit.value ? 'common.actions.save' : 'common.actions.create'))

const userFormRules = computed<FormRules<ChatUserPayload>>(() => ({
  username: [
    { whitespace: true, required: true, message: t('user.username.requiredMessage'), trigger: 'blur' },
    { min: 4, max: 64, message: t('common.validation.lengthRange', { min: 4, max: 64 }), trigger: 'blur' },
  ],
  nick_name: [
    { whitespace: true, required: true, message: t('user.name.requiredMessage'), trigger: 'blur' },
    { min: 1, max: 64, message: t('common.validation.lengthRange', { min: 1, max: 64 }), trigger: 'blur' },
  ],
  email: [{ type: 'email', message: t('user.email.invalidMessage'), trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: t('user.phone.invalidMessage'), trigger: 'blur' }],
  user_group_ids: [{ type: 'array', required: true, message: t('userGroup.requiredMessage'), trigger: 'change' }],
}))

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
            MsgSuccess(t('common.messages.saveSuccess'))
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
        ChatUserApi.postChatUser({ ...userForm, encrypted: true, password: encryptedPassword as string })
          .then(() => {
            MsgSuccess(t('common.messages.createSuccess'))
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
  Object.assign(userForm, { email: '', nick_name: '', password: '', phone: '', user_group_ids: [], username: '' })
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
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <section>
        <h4 class="mk-title-decoration mb-4">{{ t('common.labels.basicInfo') }}</h4>
        <el-form-item :label="t('user.username.label')" prop="username">
          <el-input
            v-model="userForm.username"
            :disabled="isEdit"
            maxlength="64"
            minlength="4"
            :placeholder="t('user.username.placeholder')"
            show-word-limit
          />
        </el-form-item>
        <el-form-item :label="t('user.name.label')" prop="nick_name">
          <el-input v-model="userForm.nick_name" maxlength="64" :placeholder="t('user.name.placeholder')" show-word-limit />
        </el-form-item>

        <el-form-item :label="t('user.email.label')" prop="email">
          <el-input v-model="userForm.email" type="email" :placeholder="t('user.email.placeholder')" />
        </el-form-item>

        <el-form-item :label="t('user.phone.label')" prop="phone">
          <el-input v-model="userForm.phone" maxlength="11" :placeholder="t('user.phone.placeholder')" />
        </el-form-item>

        <el-form-item v-if="!isEdit" :label="t('user.password.defaultLabel')">
          <el-input v-model="userForm.password" readonly>
            <template #suffix>
              <!-- 复制默认密码 -->
              <el-button text @click="copyText(userForm.password)" class="-mr-1">
                <MkIcon name="icon_copy_outlined" />
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </section>
      <section>
        <h4 class="mk-title-decoration mb-4 mt-4">{{ t('userGroup.title') }}</h4>
        <el-form-item :label="t('userGroup.title')" prop="user_group_ids">
          <el-select
            v-model="userForm.user_group_ids"
            class="w-full"
            :loading="userGroupOptionsLoading"
            clearable
            filterable
            multiple
            :placeholder="t('userGroup.placeholder')"
            fit-input-width
          >
            <el-option v-for="userGroup in userGroupOptions" :key="userGroup.id" :label="userGroup.name" :value="userGroup.id" />
          </el-select>
        </el-form-item>
      </section>
    </el-form>

    <template #footer>
      <!-- 取消编辑 -->
      <el-button plain @click="drawerVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交用户 -->
      <el-button :loading="userSubmitting" type="primary" @click="submitUser">
        {{ submitText }}
      </el-button>
    </template>
  </MkDrawer>
</template>
