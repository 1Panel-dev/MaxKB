<template>
  <el-dialog :title="`${!form.role_id ? $t('common.create') : $t('common.rename')}${$t('views.role.customRole')}`"
    v-model="dialogVisible" :close-on-click-modal="false" :close-on-press-escape="false" :destroy-on-close="true">
    <el-form label-position="top" ref="formRef" :rules="rules" :model="form" require-asterisk-position="right">
      <el-form-item :label="$t('views.role.roleName')" prop="role_name">
        <el-input v-model="form.role_name" maxlength="64" show-word-limit
          :placeholder="`${$t('common.inputPlaceholder')}${$t('views.role.roleName')}`" />
      </el-form-item>
      <el-form-item v-if="!form.role_id" :label="$t('views.role.inheritingRole')" prop="role_type">
        <el-select v-model="form.role_type"
          :placeholder="`${$t('common.selectPlaceholder')}${$t('views.role.inheritingRole')}`">
          <el-option v-for="(label, value) in roleTypeMap" :key="value" :label="label" :value="value" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(formRef)" :loading="loading">
          {{ !form.role_id ? $t('common.create') : $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import type { RoleItem, CreateOrUpdateParams } from '@/api/type/role'
import RoleApi from '@/api/system/role'
import { roleTypeMap } from '../index'
import {loadPermissionApi} from "@/utils/dynamics-api/permission-api.ts";

const emit = defineEmits<{
  (e: 'refresh', currentRole: RoleItem): void;
}>();

const dialogVisible = ref<boolean>(false)
const defaultForm = {
  role_name: ''
}
const form = ref<CreateOrUpdateParams>({
  ...defaultForm,
})
function open(item?: RoleItem) {
  if (item) {
    form.value = {
      role_name: item.role_name,
      role_type: item.type,
      role_id: item.id,
    }
  } else {
    form.value = { ...defaultForm }
  }
  dialogVisible.value = true
}

const formRef = ref<FormInstance>();

const rules = reactive({
  role_name: [{ required: true, message: `${t('common.inputPlaceholder')}${t('views.role.roleName')}`, trigger: 'blur' }],
  role_type: [{ required: true, message: `${t('common.selectPlaceholder')}${t('views.role.inheritingRole')}`, trigger: 'blur' }]
})

const loading = ref<boolean>(false)
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      loadPermissionApi('role').CreateOrUpdateRole(form.value, loading).then((res: any) => {
        MsgSuccess(!form.value.role_id ? t('common.createSuccess') : t('common.renameSuccess'))
        emit('refresh', res.data)
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
