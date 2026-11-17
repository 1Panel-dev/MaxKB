<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FolderItem, FolderSource } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import FolderApi from '@/api/admin/workspace/folder'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'FolderFormDialog' })

const { auth } = useStore()

const props = defineProps<{ title: string; source: FolderSource }>()

const emit = defineEmits<{ refresh: [folder: FolderItem, isEdit: boolean] }>()

const folderFormRef = useTemplateRef<FormInstance>('folderFormRef')
const visible = ref(false)
const editId = ref('')
const folderForm = reactive({ desc: '', name: '', parent_id: '' })

const rules = computed<FormRules<typeof folderForm>>(() => ({
  name: [{ message: t('common.name.requiredMessage'), whitespace: true, required: true, trigger: 'blur' }],
}))

const loading = ref(false)
function handleSubmit() {
  folderFormRef.value?.validate((valid) => {
    if (!valid) return
    loading.value = true
    const isEdit = Boolean(editId.value)
    const request = isEdit ? FolderApi.putFolder(editId.value, props.source, folderForm) : FolderApi.postFolder(props.source, folderForm)

    return request
      .then((folder) => {
        const refreshCurrentUser = isEdit ? Promise.resolve() : auth.loadAuthBaseProfile()
        return refreshCurrentUser.then(() => {
          MsgSuccess(isEdit ? t('common.messages.saveSuccess') : t('common.messages.createSuccess'))
          visible.value = false
          emit('refresh', folder, isEdit)
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open(id: string, folder?: FolderItem) {
  if (folder) {
    //  编辑当前id
    editId.value = folder?.id
    folderForm.name = folder?.name ?? ''
    folderForm.desc = folder?.desc ?? ''
    folderForm.parent_id = folder.parent_id ?? ''
  } else {
    //  给当前id添加子id
    folderForm.parent_id = id
  }

  visible.value = true
}

function resetData() {
  editId.value = ''
  folderForm.desc = ''
  folderForm.name = ''
  folderForm.parent_id = ''
  folderFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="title" @closed="resetData">
    <el-form
      ref="folderFormRef"
      :model="folderForm"
      :rules="rules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('common.name.label')" prop="name">
        <el-input
          v-model="folderForm.name"
          maxlength="64"
          :placeholder="t('common.name.placeholder')"
          show-word-limit
          @blur="folderForm.name = folderForm.name.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('common.description.label')" prop="desc">
        <el-input
          v-model="folderForm.desc"
          :placeholder="t('common.description.placeholder')"
          maxlength="128"
          show-word-limit
          :autosize="{ minRows: 3 }"
          type="textarea"
          @blur="folderForm.desc = folderForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ editId ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
