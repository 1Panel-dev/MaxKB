<template>
  <el-drawer v-model="visible" title="添加成员" size="500">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" require-asterisk-position="right">
      <el-form-item label="选择用户" prop="user_ids">
        <el-select v-model="form.user_ids" multiple filterable remote :remote-method="searchUsers" placeholder="搜索并选择用户" style="width:100%">
          <el-option v-for="u in userOptions" :key="u.id" :label="`${u.nick_name || u.username} (${u.username})`" :value="u.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">添加</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import roleApi from '@/api/system/role'
import authApi from '@/api/system/authorization'

const props = defineProps<{ currentRole?: any }>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const saving = ref(false)
const formRef = ref()
const form = reactive({ user_ids: [] as string[] })
const userOptions = ref<any[]>([])

const rules: Record<string, any> = {
  user_ids: [{ required: true, message: '请选择用户', trigger: 'blur' }],
}

function open() {
  form.user_ids = []
  visible.value = true
  formRef.value?.clearValidate()
  // Load initial user list
  const wsId = localStorage.getItem('workspace_id') || 'default'
  authApi.getUserMember(wsId).then((res: any) => {
    userOptions.value = res.data || []
  }).catch(() => { userOptions.value = [] })
}

function searchUsers(query: string) {
  const wsId = localStorage.getItem('workspace_id') || 'default'
  authApi.getUserList(wsId).then((res: any) => {
    const all = res.data || []
    userOptions.value = query
      ? all.filter((u: any) => (u.nick_name || u.username).toLowerCase().includes(query.toLowerCase()))
      : all
  }).catch(() => {})
}

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    saving.value = true
    try {
      await roleApi.CreateMember(props.currentRole?.id as string, {
        members: form.user_ids.map((id) => ({ user_id: id })),
      })
      ElMessage.success('添加成功')
      visible.value = false
      emit('refresh')
    } catch { /* handled */ }
    saving.value = false
  })
}

defineExpose({ open })
</script>
