<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import RoleApi from '@/api/admin/system/role'
import { ROLE_TYPE, type RoleItem, type RoleType, type SaveRoleRequest } from '@/api/types'
import { ROLE_TYPE_LABELS } from '@/constants/auth'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits<{ refresh: [role: RoleItem] }>()
const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const roleForm = reactive<SaveRoleRequest>({ role_name: '' })
const rules: FormRules<SaveRoleRequest> = {
  role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  role_type: [{ required: true, message: '请选择继承角色', trigger: 'change' }],
}
const roleTypeOptions = ref<RoleType[]>([
  ROLE_TYPE.ADMIN,
  ROLE_TYPE.WORKSPACE_MANAGE,
  ROLE_TYPE.USER,
])

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    RoleApi.postRole({ ...roleForm })
      .then((role) => {
        MsgSuccess(roleForm.role_id ? '重命名成功' : '创建成功')
        emit('refresh', role)
        close()
      })
      .finally(() => {
        loading.value = false
      })
  })
}
function open(role?: RoleItem) {
  if (role) {
    roleForm.role_id = role.id
    roleForm.role_name = role.role_name
    roleForm.role_type = role.type
  }
  visible.value = true
}

function close() {
  visible.value = false
  resetData()
}
function resetData() {
  roleForm.role_id = undefined
  roleForm.role_name = ''
  roleForm.role_type = undefined
  loading.value = false
  formRef.value?.clearValidate()
}
defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="roleForm.role_id ? '重命名角色' : '创建角色'"
    @closed="resetData"
  >
    <el-form ref="formRef" :model="roleForm" :rules="rules" label-position="top">
      <el-form-item label="角色名称" prop="role_name">
        <el-input
          v-model="roleForm.role_name"
          maxlength="64"
          show-word-limit
          placeholder="请输入角色名称"
        />
      </el-form-item>
      <el-form-item v-if="!roleForm.role_id" label="继承角色" prop="role_type">
        <el-select v-model="roleForm.role_type" placeholder="请选择角色">
          <el-option
            v-for="option in roleTypeOptions"
            :key="option"
            :value="option"
            :label="ROLE_TYPE_LABELS[option]"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">{{
        roleForm.role_id ? '保存' : '创建'
      }}</el-button>
    </template>
  </MkDialog>
</template>
