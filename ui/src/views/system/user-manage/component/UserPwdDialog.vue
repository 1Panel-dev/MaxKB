<template>
  <el-dialog v-model="visible" title="修改密码" width="480" destroy-on-close>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="新密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入新密码" show-password />
      </el-form-item>
      <el-form-item label="确认密码" prop="re_password">
        <el-input v-model="form.re_password" type="password" placeholder="请再次输入新密码" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import userApi from '@/api/system/user-manage'

const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const saving = ref(false)
const userId = ref('')
const formRef = ref()
const form = reactive({ password: '', re_password: '' })

const rules: Record<string, any> = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6-20 个字符', trigger: 'blur' },
  ],
  re_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: Function) => {
        if (value !== form.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

watch(visible, (v) => {
  if (!v) {
    form.password = ''
    form.re_password = ''
    formRef.value?.clearValidate()
  }
})

function open(data: any) {
  userId.value = data.id
  visible.value = true
}

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    saving.value = true
    try {
      await userApi.putUserManagePassword(userId.value, { ...form })
      ElMessage.success('密码修改成功')
      visible.value = false
      emit('refresh')
    } catch { /* handled */ }
    saving.value = false
  })
}

defineExpose({ open })
</script>
