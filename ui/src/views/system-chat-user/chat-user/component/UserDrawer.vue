<template>
  <el-drawer v-model="visible" size="60%">
    <template #header>
      <h4>{{ props.title }}</h4>
    </template>
    <h4 class="title-decoration-1 mb-16 mt-8">{{ $t('common.info') }}</h4>
    <el-form ref="userFormRef" :model="userForm" :rules="rules" label-position="top" require-asterisk-position="right"
      @submit.prevent :close-on-click-modal="false" :close-on-press-escape="false">
      <el-form-item :prop="isEdit ? '' : 'username'" :label="$t('views.login.loginForm.username.label')">
        <el-input v-model="userForm.username" :placeholder="$t('views.login.loginForm.username.placeholder')"
          maxlength="64" show-word-limit :disabled="isEdit">
        </el-input>
      </el-form-item>
      <el-form-item prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')">
        <el-input v-model="userForm.nick_name" :placeholder="$t('views.userManage.userForm.nick_name.placeholder')"
          maxlength="64" show-word-limit>
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.login.loginForm.email.label')" prop="email">
        <el-input type="email" v-model="userForm.email" :placeholder="$t('views.login.loginForm.email.placeholder')">
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.userManage.userForm.phone.label')" prop="phone">
        <el-input v-model="userForm.phone" :placeholder="$t('views.userManage.userForm.phone.placeholder')">
        </el-input>
      </el-form-item>
      <el-form-item label="默认密码" v-if="!isEdit">
        <span class="mr-8">{{ userForm.password }}</span>
        <el-button type="primary" link @click="copyClick(userForm.password)">
          <AppIcon iconName="app-copy"></AppIcon>
        </el-button>
      </el-form-item>
      <h4 class="title-decoration-1 mb-16 mt-8">{{ $t('views.chatUser.group.title') }}</h4>
      <el-form-item :label="$t('views.chatUser.group.title')" prop="user_group_ids">
        <el-select v-model="userForm.user_group_ids" multiple filterable
          :placeholder="`${$t('common.selectPlaceholder')}${$t('views.chatUser.group.title')}`"
          :loading="props.optionLoading">
          <el-option v-for="item in props.chatGroupList" :key="item.id" :label="item.name" :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click.prevent="visible = false"> {{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submit(userFormRef)" :loading="loading">
        {{ $t('common.save') }}
      </el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import userManageApi from '@/api/system/user-manage'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import type { ListItem } from '@/api/type/common'
import { copyClick } from '@/utils/clipboard'
import {loadPermissionApi} from "@/utils/dynamics-api/permission-api.ts";

const props = defineProps<{
  title: string,
  optionLoading: boolean,
  chatGroupList: ListItem[],
}>()

const emit = defineEmits(['refresh'])

const userFormRef = ref()
const userForm = ref<any>({
  username: '',
  email: '',
  password: '',
  phone: '',
  nick_name: '',
  user_group_ids: []
})

const rules = reactive({
  username: [
    {
      required: true,
      message: t('views.login.loginForm.username.requiredMessage'),
      trigger: 'blur',
    },
    {
      min: 4,
      max: 64,
      message: t('views.login.loginForm.username.lengthMessage'),
      trigger: 'blur',
    },
  ],
  nick_name: [
    {
      required: true,
      message: t('views.userManage.userForm.nick_name.placeholder'),
      trigger: 'blur',
    },
    {
      min: 1,
      max: 64,
      message: t('views.userManage.userForm.nick_name.lengthMessage'),
      trigger: 'blur',
    },
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: t('views.userManage.userForm.phone.invalidMessage'),
      trigger: 'blur',
    },
  ],
  user_group_ids: [
    {
      type: 'array',
      required: true,
      message: t('views.chatUser.group.requiredMessage'),
      trigger: 'change',
    },
  ],
})
const visible = ref<boolean>(false)
const loading = ref(false)
const isEdit = ref(false)

watch(visible, (bool) => {
  if (!bool) {
    userForm.value = {
      username: '',
      email: '',
      password: '',
      phone: '',
      nick_name: '',
      user_group_ids: []
    }
    isEdit.value = false
    userFormRef.value?.clearValidate()
  }
})

const open = (data: any) => {
  if (data) {
    userForm.value['id'] = data.id
    userForm.value.username = data.username
    userForm.value.email = data.email
    userForm.value.phone = data.phone
    userForm.value.nick_name = data.nick_name
    userForm.value.user_group_ids = data.user_group_ids
    isEdit.value = true
  } else {
    userManageApi.getSystemDefaultPassword().then((res: any) => {
      userForm.value.password = res.data.password
    })
  }

  visible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (isEdit.value) {
        loadPermissionApi('chatUser').putUserManage(userForm.value.id, userForm.value, loading).then(() => {
          emit('refresh')
          MsgSuccess(t('common.editSuccess'))
          visible.value = false
        })
      } else {
        loadPermissionApi('chatUser').postUserManage(userForm.value, loading).then(() => {
          emit('refresh')
          MsgSuccess(t('common.createSuccess'))
          visible.value = false
        })
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped>

</style>
