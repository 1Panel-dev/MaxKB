<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ListItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import ChatGroupsApi from '@/api/admin/system/chat-management/chat-user-groups'
import { MsgSuccess } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ refresh: [groupId?: string] }>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const groupForm = reactive<{ id?: string; name: string }>({ name: '' })
const formRules = computed<FormRules>(() => ({
  name: [{ whitespace: true, required: true, message: t('userGroup.name.requiredMessage'), trigger: 'blur' }],
}))

function open(group?: ListItem) {
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
    ChatGroupsApi.postChatUserGroup({ ...groupForm })
      .then(() => {
        MsgSuccess(t(groupForm.id ? 'common.messages.renameSuccess' : 'common.messages.createSuccess'))
        emit('refresh', groupForm?.id || undefined)
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
  <MkDialog v-model="visible" :title="t(groupForm.id ? 'userGroup.renameTitle' : 'userGroup.createTitle')" @closed="resetData">
    <el-form ref="formRef" :model="groupForm" :rules="formRules" :validate-on-rule-change="false" label-position="top" @submit.prevent>
      <el-form-item :label="t('userGroup.name.label')" prop="name">
        <el-input v-model="groupForm.name" maxlength="128" :placeholder="t('userGroup.name.placeholder')" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消用户组编辑 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存或创建用户组 -->
      <el-button type="primary" :loading="loading" @click="submit">
        {{ t(groupForm.id ? 'common.actions.save' : 'common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
