<template>
  <el-drawer v-model="visible" size="60%">
    <template #header>
      <h4>{{ title }}</h4>
    </template>
    <h4 class="title-decoration-1 mb-16 mt-8">{{ $t('common.info') }}</h4>
    <el-form
      ref="userFormRef"
      :model="userForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <el-form-item
        :prop="isEdit ? '' : 'username'"
        :label="$t('views.login.loginForm.username.label')"
      >
        <el-input
          v-model="userForm.username"
          :placeholder="$t('views.login.loginForm.username.placeholder')"
          maxlength="20"
          show-word-limit
          :disabled="isEdit"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.userManage.userForm.nick_name.label')">
        <el-input
          v-model="userForm.nick_name"
          :placeholder="$t('views.userManage.userForm.nick_name.placeholder')"
          maxlength="64"
          show-word-limit
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.userManage.userForm.email.label')" prop="email">
        <el-input
          type="email"
          v-model="userForm.email"
          :placeholder="$t('views.userManage.userForm.email.placeholder')"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.userManage.userForm.phone.label')">
        <el-input
          v-model="userForm.phone"
          :placeholder="$t('views.userManage.userForm.phone.placeholder')"
        >
        </el-input>
      </el-form-item>
      <el-form-item
        :label="$t('views.userManage.form.password.label')"
        prop="password"
        v-if="!isEdit"
      >
        <el-input
          type="password"
          v-model="userForm.password"
          :placeholder="$t('views.userManage.form.password.placeholder')"
          show-password
        >
        </el-input>
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
import {ref, reactive, watch} from 'vue'
import type {FormInstance} from 'element-plus'
import userManageApi from '@/api/system/chat-user'
import {MsgSuccess} from '@/utils/message'
import {t} from '@/locales'

const props = defineProps({
  title: String,
})

const emit = defineEmits(['refresh'])

const userFormRef = ref()
const userForm = ref<any>({
  username: '',
  email: '',
  password: '',
  phone: '',
  nick_name: '',
})

const rules = reactive({
  username: [
    {
      required: true,
      message: t('views.userManage.form.username.requiredMessage'),
      trigger: 'blur',
    },
    {
      min: 6,
      max: 20,
      message: t('views.userManage.form.username.lengthMessage'),
      trigger: 'blur',
    },
  ],
  email: [
    {
      required: true,
      message: t('views.userManage.form.email.requiredMessage'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: t('views.userManage.form.password.requiredMessage'),
      trigger: 'blur',
    },
    {
      min: 6,
      max: 20,
      message: t('views.userManage.form.password.lengthMessage'),
      trigger: 'blur',
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
    userForm.value.password = data.password
    userForm.value.phone = data.phone
    userForm.value.nick_name = data.nick_name
    isEdit.value = true
  }
  visible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (isEdit.value) {
        userManageApi.putUserManage(userForm.value.id, userForm.value, loading).then((res) => {
          emit('refresh')
          MsgSuccess(t('common.editSuccess'))
          visible.value = false
        })
      } else {
        userManageApi.postUserManage(userForm.value, loading).then((res) => {
          emit('refresh')
          MsgSuccess(t('common.createSuccess'))
          visible.value = false
        })
      }
    }
  })
}

defineExpose({open})
</script>
<style lang="scss" scoped></style>
