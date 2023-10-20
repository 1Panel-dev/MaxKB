<template>
  <el-dialog
    v-model="dialogVisible"
    :close-on-press-escape="false"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    width="600"
  >
    <template #header="{ titleId, titleClass }">
      <h4 :id="titleId" :class="titleClass">添加成员</h4>
      <div class="dialog-sub-title">成员登录后可以访问到您授权的数据。</div>
    </template>

    <el-form
      ref="addMemberFormRef"
      :model="memberForm"
      label-position="top"
      :rules="rules"
      @submit.prevent
    >
      <el-form-item label="用户名/邮箱" prop="users">
        <tags-input
          v-model:tags="memberForm.users"
          v-model:tag="memberForm.user"
          placeholder="请输入成员的用户名或邮箱，若需添加多个成员请使用回车分割。"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitMember(addMemberFormRef)"> 添加 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import TeamApi from '@/api/team'

const emit = defineEmits(['refresh'])

const dialogVisible = ref<boolean>(false)

const memberForm = ref({
  users: [],
  user: ''
})

const addMemberFormRef = ref<FormInstance>()

const loading = ref<boolean>(false)

const validateUsers = (rule: any, value: any, callback: any) => {
  if (value?.length == 0 && !memberForm.value.user) {
    callback(new Error('请输入用户名/邮箱'))
  } else {
    callback()
  }
}
const rules = ref<FormRules>({
  users: [{ type: 'array', validator: validateUsers }]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    memberForm.value = {
      users: [],
      user: ''
    }
  }
})

const open = () => {
  dialogVisible.value = true
}
const submitMember = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      loading.value = true
      const obj: any = {
        username_or_email: memberForm.value.users?.length
          ? memberForm.value.users.toString()
          : memberForm.value.user
      }
      TeamApi.postCreatTeamMember(obj).then(() => {
        MsgSuccess('提交成功')
        emit('refresh')
        dialogVisible.value = false
      })
    } else {
      console.log('error submit!')
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scope></style>
