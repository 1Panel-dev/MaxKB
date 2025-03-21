<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
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
        :label="$t('views.user.userForm.form.username.label')"
      >
        <el-input
          v-model="userForm.username"
          :placeholder="$t('views.user.userForm.form.username.placeholder')"
          maxlength="20"
          show-word-limit
          :disabled="isEdit"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.user.userForm.form.nick_name.label')">
        <el-input
          v-model="userForm.nick_name"
          :placeholder="$t('views.user.userForm.form.nick_name.placeholder')"
          maxlength="64"
          show-word-limit
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.user.userForm.form.email.label')" prop="email">
        <el-input
          type="email"
          v-model="userForm.email"
          :placeholder="$t('views.user.userForm.form.email.placeholder')"
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.user.userForm.form.phone.label')">
        <el-input
          v-model="userForm.phone"
          :placeholder="$t('views.user.userForm.form.phone.placeholder')"
        >
        </el-input>
      </el-form-item>
      <el-form-item
        :label="$t('views.user.userForm.form.password.label')"
        prop="password"
        v-if="!isEdit"
      >
        <el-input
          type="password"
          v-model="userForm.password"
          :placeholder="$t('views.user.userForm.form.password.placeholder')"
          show-password
        >
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(userFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import userApi from '@/api/user-manage'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
const props = defineProps({
  title: String
})

const emit = defineEmits(['refresh'])

const userFormRef = ref()
const userForm = ref<any>({
  username: '',
  email: '',
  password: '',
  phone: '',
  nick_name: ''
})

const rules = reactive({
  username: [
    {
      required: true,
      message: t('views.user.userForm.form.username.requiredMessage'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('views.user.userForm.form.username.lengthMessage'),
      trigger: 'blur'
    }
  ],
  email: [
    {
      required: true,
      message: t('views.user.userForm.form.email.requiredMessage'),
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: t('views.user.userForm.form.password.requiredMessage'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('views.user.userForm.form.password.lengthMessage'),
      trigger: 'blur'
    }
  ]
})
const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const isEdit = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    userForm.value = {
      username: '',
      email: '',
      password: '',
      phone: '',
      nick_name: ''
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
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (isEdit.value) {
        userApi.putUserManage(userForm.value.id, userForm.value, loading).then((res) => {
          emit('refresh')
          MsgSuccess(t('common.editSuccess'))
          dialogVisible.value = false
        })
      } else {
        userApi.postUserManage(userForm.value, loading).then((res) => {
          emit('refresh')
          MsgSuccess(t('common.createSuccess'))
          dialogVisible.value = false
        })
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
