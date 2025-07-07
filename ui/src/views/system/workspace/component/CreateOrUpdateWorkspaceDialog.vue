<template>
  <el-dialog :title="`${!form.id ? $t('common.create') : $t('common.rename')}${$t('views.workspace.title')}`"
    v-model="dialogVisible" :close-on-click-modal="false" :close-on-press-escape="false" :destroy-on-close="true">
    <el-form label-position="top" ref="formRef" :rules="rules" :model="form" require-asterisk-position="right" @submit.prevent>
      <el-form-item :label="$t('views.workspace.name')" prop="name">
        <el-input v-model="form.name" maxlength="64" show-word-limit
          :placeholder="`${$t('common.inputPlaceholder')}${$t('views.workspace.name')}`" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(formRef)" :loading="loading">
          {{ !form.id ? $t('common.create') : $t('common.save') }}
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
import type { WorkspaceItem } from '@/api/type/workspace'
import WorkspaceApi from '@/api/workspace/workspace'
import {loadPermissionApi} from "@/utils/dynamics-api/permission-api.ts";

const emit = defineEmits<{
  (e: 'refresh', currentWorkspace: WorkspaceItem): void;
}>();

const dialogVisible = ref<boolean>(false)
const defaultForm = {
  name: ''
}
const form = ref<WorkspaceItem>({
  ...defaultForm,
})
function open(item?: WorkspaceItem) {
  if (item) {
    form.value = { id: item.id, name: item.name }
  } else {
    form.value = { ...defaultForm }
  }
  dialogVisible.value = true
}

const formRef = ref<FormInstance>();

const rules = reactive({
  name: [{ required: true, message: `${t('common.inputPlaceholder')}${t('views.workspace.name')}`, trigger: 'blur' }],
})

const loading = ref<boolean>(false)
const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      loadPermissionApi('workspace').CreateOrUpdateWorkspace(form.value, loading).then((res: any) => {
        MsgSuccess(!form.value.id ? t('common.createSuccess') : t('common.renameSuccess'))
        emit('refresh', res.data)
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
