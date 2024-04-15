<template>
  <el-dialog :title="title" v-model="dialogVisible">
    <el-form
      ref="userFormRef"
      :model="userForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :prop="isEdit ? '' : 'username'" label="用户名">
        <el-input
          v-model="userForm.username"
          placeholder="请输入用户名"
          maxlength="20"
          show-word-limit
          :disabled="isEdit"
        >
        </el-input>
      </el-form-item>
      <el-form-item label="姓名">
        <el-input
          v-model="userForm.nick_name"
          placeholder="请输入姓名"
          maxlength="64"
          show-word-limit
        >
        </el-input>
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input type="email" v-model="userForm.email" placeholder="请输入邮箱"> </el-input>
      </el-form-item>
      <el-form-item label="手机号">
        <el-input type="email" v-model="userForm.phone" placeholder="请输入手机号"> </el-input>
      </el-form-item>
      <el-form-item label="登录密码" prop="password" v-if="!isEdit">
        <el-input
          type="password"
          v-model="userForm.password"
          placeholder="请输入密码"
          show-password
        >
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(userFormRef)" :loading="loading"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import userApi from '@/api/user-manage'
import { MsgSuccess } from '@/utils/message'

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
    { required: true, message: '请输入用户名', trigger: 'blur' },
    {
      min: 6,
      max: 20,
      message: '长度在 6 到 20 个字符',
      trigger: 'blur'
    }
  ],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: '长度在 6 到 20 个字符',
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
          MsgSuccess('编辑成功')
          dialogVisible.value = false
        })
      } else {
        userApi.postUserManage(userForm.value, loading).then((res) => {
          emit('refresh')
          MsgSuccess('创建成功')
          dialogVisible.value = false
        })
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
