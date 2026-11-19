<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WorkspaceItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import WorkspaceApi from '@/api/admin/system/workspace'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateOrUpdateWorkspaceDialog' })

const emit = defineEmits<{ refresh: [workspaceId?: string] }>()
const { t } = useI18n({ useScope: 'global' })

const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const workspaceForm = reactive<WorkspaceItem>({ name: '' })
const workspaceRules = computed<FormRules<WorkspaceItem>>(() => ({
  name: [{ whitespace: true, required: true, message: t('workspace.name.requiredMessage'), trigger: 'blur' }],
}))
function open(workspace?: WorkspaceItem) {
  if (workspace) {
    workspaceForm.id = workspace?.id
    workspaceForm.name = workspace?.name
  }
  dialogVisible.value = true
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    WorkspaceApi.postWorkspace({ ...workspaceForm })
      .then(() => {
        MsgSuccess(workspaceForm.id ? t('common.messages.renameSuccess') : t('common.messages.createSuccess'))
        emit('refresh', workspaceForm?.id || undefined)
        dialogVisible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function resetData() {
  Object.assign(workspaceForm, { id: undefined, name: '' })
  loading.value = false
  formRef.value?.clearValidate()
}
defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="workspaceForm.id ? t('workspace.renameTitle') : t('workspace.createTitle')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="workspaceForm"
      :rules="workspaceRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('workspace.name.label')" prop="name">
        <el-input v-model="workspaceForm.name" maxlength="64" :placeholder="t('workspace.name.placeholder')" show-word-limit />
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消工作空间编辑 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存或创建工作空间 -->
      <el-button type="primary" :loading="loading" @click="submit">
        {{ workspaceForm.id ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
