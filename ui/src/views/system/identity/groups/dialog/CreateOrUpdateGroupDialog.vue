<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SystemUserGroup } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import UserGroupsApi from '@/api/admin/system/user-groups'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits<{ refresh: [group: SystemUserGroup] }>()
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ workspaceId: string }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const groupForm = reactive<{ id?: string; name: string }>({ name: '' })
const formRules = computed<FormRules>(() => ({
  name: [{ whitespace: true, required: true, message: t('userGroup.name.requiredMessage'), trigger: 'blur' }],
}))

function open(group?: { id: string; name: string }) {
  if (group) {
    groupForm.id = group?.id
    groupForm.name = group?.name
  }
  visible.value = true
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    UserGroupsApi.postSystemUserGroup(props.workspaceId, { id: groupForm.id, name: groupForm.name })
      .then((group) => {
        MsgSuccess(groupForm.id ? t('common.messages.renameSuccess') : t('common.messages.createSuccess'))
        emit('refresh', group)
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function resetData() {
  Object.assign(groupForm, { id: undefined, name: '' })
  loading.value = false
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="groupForm.id ? t('userGroup.renameTitle') : t('userGroup.createTitle')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="groupForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('userGroup.name.label')" prop="name">
        <el-input v-model="groupForm.name" maxlength="128" :placeholder="t('userGroup.name.placeholder')" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消用户组编辑 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存或创建用户组 -->
      <el-button type="primary" :loading="loading" @click="submit">
        {{ groupForm.id ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
