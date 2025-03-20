<template>
  <el-dialog :title="$t('views.user.setting.updatePwd')" v-model="dialogVisible">
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
      <el-form-item :label="$t('views.user.userForm.form.new_password.label')" prop="password">
        <el-input
          type="password"
          v-model="userForm.password"
          :placeholder="$t('views.user.userForm.form.new_password.placeholder')"
          show-password
        >
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('views.user.userForm.form.re_password.label')" prop="re_password">
        <el-input
          type="password"
          v-model="userForm.re_password"
          :placeholder="$t('views.user.userForm.form.re_password.placeholder')"
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
import useStore from '@/stores'
import type { FormInstance, FormRules } from 'element-plus'
import type { ResetPasswordRequest } from '@/api/type/user'
import userApi from '@/api/user-manage'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
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
      message: t('views.user.userForm.form.new_password.requiredMessage'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('views.user.userForm.form.password.lengthMessage'),
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: t('views.user.userForm.form.re_password.requiredMessage'),
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: t('views.user.userForm.form.password.lengthMessage'),
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (userFormRef.value.password != userFormRef.value.re_password) {
          callback(new Error(t('views.user.userForm.form.re_password.validatorMessage')))
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
        MsgSuccess(t('views.user.tip.updatePwdSuccess'))
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
