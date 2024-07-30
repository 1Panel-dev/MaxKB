<template>
  <el-dialog title="修改用户密码" v-model="dialogVisible">
    <el-form
      ref="userFormRef"
      :model="userForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="新密码" prop="password">
        <el-input
          type="password"
          v-model="userForm.password"
          placeholder="请输入新密码"
          show-password
        >
        </el-input>
      </el-form-item>
      <el-form-item label="确认密码" prop="re_password">
        <el-input
          type="password"
          v-model="userForm.re_password"
          placeholder="请输入确认密码"
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
import useStore from '@/stores'
import type { FormInstance, FormRules } from 'element-plus'
import type { ResetPasswordRequest } from '@/api/type/user'
import userApi from '@/api/user-manage'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits(['refresh'])

const { user } = useStore()

const userFormRef = ref()
const userForm = ref<any>({
  password: '',
  re_password: ''
})

const rules = reactive<FormRules<ResetPasswordRequest>>({
  password: [
    {
      required: true,
      message: '请输入新密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: '长度在 6 到 20 个字符',
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: '请输入确认密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: '长度在 6 到 20 个字符',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (userFormRef.value.password != userFormRef.value.re_password) {
          callback(new Error('密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})
const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const userId = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    userForm.value = {
      password: '',
      re_password: ''
    }
  }
})

const open = (data: any) => {
  userId.value = data.id
  dialogVisible.value = true
  userFormRef.value?.clearValidate()
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      userApi.putUserManagePassword(userId.value, userForm.value, loading).then((res) => {
        emit('refresh')
        user.profile()
        MsgSuccess('修改用户密码成功')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
