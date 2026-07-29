<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

export interface UserFormValue {
  email: string
  name: string
  phone: string
  role: string
  username: string
}

const props = defineProps<{
  modelValue: boolean
  user?: UserFormValue
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [value: UserFormValue]
}>()

const formRef = ref<FormInstance>()
const userForm = reactive<UserFormValue>({
  email: '',
  name: '',
  phone: '',
  role: '普通用户',
  username: '',
})

const dialogTitle = computed(() => (props.user ? '编辑用户' : '创建用户'))

const userFormRules: FormRules<UserFormValue> = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' },
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
}

watch(
  () => [props.modelValue, props.user] as const,
  ([visible, user]) => {
    if (!visible) return

    Object.assign(userForm, {
      email: user?.email ?? '',
      name: user?.name ?? '',
      phone: user?.phone ?? '',
      role: user?.role ?? '普通用户',
      username: user?.username ?? '',
    })
    formRef.value?.clearValidate()
  },
  { immediate: true },
)

function closeDialog() {
  emit('update:modelValue', false)
}

async function submitUser() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  emit('submit', { ...userForm })
  closeDialog()
}
</script>

<template>
  <el-dialog
    :model-value="props.modelValue"
    :title="dialogTitle"
    width="600"
    align-center
    destroy-on-close
    @close="closeDialog"
  >
    <el-form
      ref="formRef"
      :model="userForm"
      :rules="userFormRules"
      label-position="top"
      class="grid grid-cols-2 gap-x-2"
    >
      <el-form-item label="姓名" prop="name" class="col-span-2">
        <el-input v-model="userForm.name" placeholder="请输入姓名" />
      </el-form-item>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="userForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="userForm.role" class="w-full">
          <el-option label="普通用户" value="普通用户" />
          <el-option label="工作空间管理员" value="工作空间管理员" />
        </el-select>
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="userForm.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="userForm.phone" placeholder="请输入手机号" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="closeDialog">取消</el-button>
      <el-button type="primary" @click="submitUser">确认</el-button>
    </template>
  </el-dialog>
</template>
