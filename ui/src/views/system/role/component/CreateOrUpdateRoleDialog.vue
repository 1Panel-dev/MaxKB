<template>
  <el-dialog
    v-model="visible"
    :title="`${isEdit ? '重命名' : '创建'}自定义角色`"
    width="480"
    destroy-on-close
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" require-asterisk-position="right">
      <el-form-item label="角色名称" prop="role_name">
        <el-input v-model="form.role_name" maxlength="64" show-word-limit placeholder="请输入角色名称" />
      </el-form-item>
      <el-form-item v-if="!isEdit" label="继承角色" prop="role_type">
        <el-select v-model="form.role_type" placeholder="请选择继承角色" style="width:100%">
          <el-option
            v-for="opt in createRoleTypeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <div class="text-xs text-gray-400 mt-1">
          新建角色将继承所选内置角色的权限模板，后续可自定义调整
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ isEdit ? '保存' : '创建' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import roleApi from '@/api/system/role'
import { createRoleTypeOptions } from '../index'

const emit = defineEmits<{ refresh: [role?: any] }>()

const visible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const formRef = ref()
const form = reactive({ role_name: '', role_type: '', role_id: '' })

const rules: Record<string, any> = {
  role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  role_type: [{ required: true, message: '请选择继承角色', trigger: 'blur' }],
}

function open(item?: any) {
  if (item) {
    form.role_name = item.role_name
    form.role_type = item.type
    form.role_id = item.id
    isEdit.value = true
  } else {
    form.role_name = ''
    form.role_type = ''
    form.role_id = ''
    isEdit.value = false
  }
  visible.value = true
  formRef.value?.clearValidate()
}

async function submit() {
  if (!formRef.value) return
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
  } catch {
    return
  }

  saving.value = true
  try {
    const payload = isEdit.value
      ? { role_name: form.role_name, role_id: form.role_id }
      : { role_name: form.role_name, role_type: form.role_type }
    const res = await roleApi.CreateOrUpdateRole(payload)
    ElMessage.success(isEdit.value ? '重命名成功' : '创建成功')
    visible.value = false
    emit('refresh', res.data)
  } catch (e) {
    console.error('[role] create failed:', e)
  }
  saving.value = false
}

defineExpose({ open })
</script>
