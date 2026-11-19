<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { RoleItem, RolePayload, RoleType } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { ROLE_TYPE } from '@/api/enums'
import RoleApi from '@/api/admin/system/role'
import { ROLE_TYPE_LABELS } from '@/constants'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits<{ refresh: [role: RoleItem] }>()
const { t } = useI18n({ useScope: 'global' })
const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const roleForm = reactive<RolePayload>({ role_name: '' })
const rules = computed<FormRules<RolePayload>>(() => ({
  role_name: [{ whitespace: true, required: true, message: t('role.name.requiredMessage'), trigger: 'blur' }],
  role_type: [{ required: true, message: t('role.inheritedRole.requiredMessage'), trigger: 'change' }],
}))
const roleTypeOptions = ref<RoleType[]>([ROLE_TYPE.ADMIN, ROLE_TYPE.WORKSPACE_MANAGE, ROLE_TYPE.USER])

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    RoleApi.postRole({ ...roleForm })
      .then((role) => {
        MsgSuccess(roleForm.role_id ? t('common.messages.renameSuccess') : t('common.messages.createSuccess'))
        emit('refresh', role)
        visible.value = false
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
  <MkDialog v-model="visible" :title="roleForm.role_id ? t('role.renameTitle') : t('role.createTitle')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="roleForm"
      :rules="rules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('role.name.label')" prop="role_name">
        <el-input v-model="roleForm.role_name" maxlength="64" show-word-limit :placeholder="t('role.name.placeholder')" />
      </el-form-item>
      <el-form-item v-if="!roleForm.role_id" :label="t('role.inheritedRole.label')" prop="role_type">
        <el-select v-model="roleForm.role_type" :placeholder="t('user.role.placeholder')">
          <el-option v-for="option in roleTypeOptions" :key="option" :value="option" :label="ROLE_TYPE_LABELS[option]" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消角色编辑 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存或创建角色 -->
      <el-button type="primary" :loading="loading" @click="submit">
        {{ roleForm.role_id ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
