<template>
  <el-drawer v-model="visible" size="550">
    <template #header>
      <h4>{{ title }}</h4>
    </template>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <h4 class="text-sm font-semibold mb-3" style="color:var(--mk-N900)">基本信息</h4>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" maxlength="64" show-word-limit :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="昵称" prop="nick_name">
        <el-input v-model="form.nick_name" placeholder="请输入昵称" maxlength="64" show-word-limit />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="form.phone" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="默认密码" v-if="!isEdit">
        <span class="text-sm">{{ form.password }}</span>
      </el-form-item>

      <h4 class="text-sm font-semibold mb-3 mt-6" style="color:var(--mk-N900)">角色设置</h4>
      <div v-for="(rs, idx) in form.roleSettings" :key="idx" class="flex items-start gap-2 mb-3">
        <el-form-item
          :label="idx === 0 ? '角色' : ''"
          :prop="`roleSettings.${idx}.role_id`"
          :rules="roleRules"
          class="flex-1"
        >
          <el-select
            v-model="rs.role_id"
            placeholder="请选择角色"
            filterable
            style="width:100%"
            @change="onRoleChange(idx)"
          >
            <el-option
              v-for="r in roleOptions"
              :key="r.id"
              :label="r.role_name"
              :value="r.id"
              :disabled="selectedRoleIds.includes(r.id) && selectedRoleIds.indexOf(r.id) !== idx"
            />
          </el-select>
        </el-form-item>
        <el-button
          v-if="form.roleSettings.length > 1"
          text
          type="danger"
          size="small"
          :style="{ marginTop: idx === 0 ? '32px' : '2px' }"
          @click="form.roleSettings.splice(idx, 1)"
        >
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
      <el-button text type="primary" size="small" @click="form.roleSettings.push({ role_id: '' })">
        + 添加角色
      </el-button>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import userApi from '@/api/system/user-manage'
import roleApi from '@/api/system/role'

const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const title = ref('')
const formRef = ref()

const form = reactive({
  username: '',
  nick_name: '',
  email: '',
  phone: '',
  password: '',
  roleSettings: [{ role_id: '' }] as { role_id: string }[],
})
const userId = ref('')
const allRoles = ref<any[]>([])

const roleOptions = computed(() => {
  // Flatten internal + custom roles for selection
  return allRoles.value
})

const selectedRoleIds = computed(() => form.roleSettings.map((rs: any) => rs.role_id).filter(Boolean))

const roleRules = [{ required: true, message: '请选择角色', trigger: 'change' }]

const rules: Record<string, any> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 64, message: '用户名长度为 4-64 个字符', trigger: 'blur' },
  ],
  nick_name: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 1, max: 64, message: '昵称长度为 1-64 个字符', trigger: 'blur' },
  ],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }],
}

watch(visible, (v) => {
  if (!v) {
    form.username = ''
    form.nick_name = ''
    form.email = ''
    form.phone = ''
    form.password = ''
    userId.value = ''
    isEdit.value = false
    form.roleSettings = [{ role_id: '' }]
    formRef.value?.clearValidate()
  }
})

async function loadRoles() {
  try {
    const res = await roleApi.getRoleList()
    const internal = res.data?.internal_role || []
    const custom = res.data?.custom_role || []
    allRoles.value = [...internal, ...custom]
  } catch { allRoles.value = [] }
}

function onRoleChange(idx: number) {
  // Trigger reactivity
}

function open(data?: any) {
  loadRoles()
  if (data) {
    userId.value = data.id
    form.username = data.username
    form.nick_name = data.nick_name
    form.email = data.email
    form.phone = data.phone || ''
    isEdit.value = true
    title.value = '编辑用户'

    // Populate role settings from existing data
    if (data.role_setting?.length) {
      form.roleSettings = data.role_setting.map((rs: any) => ({ role_id: rs.role_id }))
    } else {
      form.roleSettings = [{ role_id: '' }]
    }
  } else {
    title.value = '创建用户'
    form.roleSettings = [{ role_id: '' }]
    userApi.getSystemDefaultPassword().then((res: any) => {
      form.password = res.data?.password || 'MaxKB@123..'
    })
  }
  visible.value = true
}

async function submit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请检查表单输入')
    return
  }
  saving.value = true
  try {
    const payload = {
      username: form.username,
      nick_name: form.nick_name,
      email: form.email,
      phone: form.phone,
      password: form.password,
      role_setting: (form.roleSettings || [])
        .filter((rs: any) => rs.role_id)
        .map((rs: any) => ({
          role_id: rs.role_id,
          workspace_ids: [],
        })),
    }
    if (isEdit.value) {
      await userApi.putUserManage(userId.value, payload)
      ElMessage.success('编辑成功')
    } else {
      await userApi.postUserManage(payload)
      ElMessage.success('创建成功')
    }
    visible.value = false
    emit('refresh')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败，请稍后重试')
    console.error('[user] submit failed:', e)
  }
  saving.value = false
}

defineExpose({ open })
</script>
